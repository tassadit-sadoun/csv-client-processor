import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from unittest.mock import patch
import pathlib
import shutil
import io

from main import app
from database.base_class import Base
from database.db import db_context
from models import Client, ImportJob, JobStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
connection = engine.connect()
Base.metadata.create_all(bind=connection)

TestingSessionLocal = sessionmaker(
    bind=connection,
    autocommit=False,
    autoflush=False,
)


def override_db_context():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[db_context] = override_db_context
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    yield
    Base.metadata.drop_all(bind=connection)
    connection.close()


@pytest.fixture(scope="function")
def seed_clients():
    db = TestingSessionLocal()
    clients = [
        Client(
            name="Alice",    # type: ignore[call-arg]
            email="alice@example.com",   # type: ignore[call-arg]
            birth_date=date(1990, 1, 1),  # type: ignore[call-arg]
        ),
        Client(
            name="Bob",  # type: ignore[call-arg]
            email="bob@example.com",  # type: ignore[call-arg]
            birth_date=date(1985, 5, 20),  # type: ignore[call-arg]
        ),
        Client(
            name="Charlie",  # type: ignore[call-arg]
            email="charlie@example.com",  # type: ignore[call-arg]
            birth_date=date(2000, 12, 31),  # type: ignore[call-arg]
        ),
    ]
    db.add_all(clients)
    db.commit()
    yield
    db.query(Client).delete()
    db.commit()
    db.close()


@pytest.fixture(scope="function")
def seed_import_jobs():
    db = TestingSessionLocal()
    job1 = ImportJob(
        id=uuid4(),  # type: ignore[call-arg]
        status=JobStatus.completed,  # type: ignore[call-arg]
        row_stats={"total": 100, "valid": 90, "errors": 10},  # type: ignore[call-arg]
    )
    job2 = ImportJob(
        id=uuid4(),  # type: ignore[call-arg]
        status=JobStatus.in_progress,  # type: ignore[call-arg]
        row_stats=None,  # type: ignore[call-arg]
    )
    db.add_all([job1, job2])
    db.commit()
    yield job1, job2
    db.query(ImportJob).delete()
    db.commit()
    db.close()


def test_get_clients_success(seed_clients):
    response = client.get("/api/clients?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["total_pages"] == 2
    assert len(data["clients"]) == 2


def test_get_clients_page_2(seed_clients):
    response = client.get("/api/clients?page=2&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["clients"]) == 1


def test_get_clients_page_too_high():
    response = client.get("/api/clients?page=5&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 5
    assert data["clients"] == []


def test_get_clients_invalid_per_page():
    response = client.get("/api/clients?page=1&per_page=0")
    assert response.status_code == 422


def test_get_clients_invalid_page():
    response = client.get("/api/clients?page=-1&per_page=2")
    assert response.status_code == 422


def test_get_clients_empty():
    db = TestingSessionLocal()
    db.query(Client).delete()
    db.commit()
    db.close()
    response = client.get("/api/clients?page=1&per_page=10")
    assert response.status_code == 200
    data = response.json()
    assert data["clients"] == []
    assert data["page"] == 1
    assert data["total_pages"] == 0


def test_get_import_status_success(seed_import_jobs):
    job1, _ = seed_import_jobs
    response = client.get(f"/api/imports/{job1.id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == str(job1.id)
    assert data["status"] == job1.status.name.upper()
    assert data["total"] == 100
    assert data["valid"] == 90
    assert data["errors"] == 10


def test_get_import_status_in_progress(seed_import_jobs):
    _, job2 = seed_import_jobs
    response = client.get(f"/api/imports/{job2.id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == str(job2.id)
    assert data["status"] == job2.status.name.upper()
    assert data["total"] == 0
    assert data["valid"] == 0
    assert data["errors"] == 0


@pytest.fixture(autouse=True)
def cleanup_shared_dir():
    shared_dir = pathlib.Path("/shared_data")
    yield
    if shared_dir.exists():
        for f in shared_dir.iterdir():
            try:
                if f.is_file():
                    f.unlink()
                elif f.is_dir():
                    shutil.rmtree(f)
            except Exception as e:
                print(f"Failed to clean up file: {f} - {e}")


def test_get_import_status_not_found():
    fake_uuid = uuid4()
    response = client.get(f"/api/imports/{fake_uuid}/status")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Import job not found"


# --- Tests ---
@patch("routers.imports.run_import_job.delay")
def test_import_clients_success(mock_delay):
    content = b"name,email,birth_date\nAlice,alice@example.com,1990-01-01"
    file = {"file": ("clients.csv", io.BytesIO(content), "text/csv")}
    
    response = client.post("/api/imports", files=file)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    mock_delay.assert_called_once()


@patch("routers.imports.run_import_job.delay")
def test_import_clients_invalid_file_save(mock_delay, monkeypatch):
    monkeypatch.setattr("os.makedirs", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("fail")))
    content = b"test"
    file = {"file": ("fail.csv", io.BytesIO(content), "text/csv")}
    response = client.post("/api/imports", files=file)

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to save uploaded file."


@patch("routers.imports.run_import_job.delay",
        side_effect=Exception("Dispatch failed")
    )
def test_import_clients_dispatch_fails(mock_delay):
    content = b"name,email,birth_date\nAlice,alice@example.com,1990-01-01"
    file = {"file": ("clients.csv", io.BytesIO(content), "text/csv")}
    response = client.post("/api/imports", files=file)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to start import job."


def test_import_clients_missing_file():
    response = client.post("/api/imports", files={})
    assert response.status_code == 422