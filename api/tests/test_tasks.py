import pytest
from celery.exceptions import Retry
from unittest.mock import patch, MagicMock
from tasks import run_import_job


@pytest.fixture
def mock_session_local():
    with patch("tasks.SessionLocal") as mock:
        mock_instance = MagicMock()
        mock.return_value.__enter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_process_csv():
    with patch("tasks.process_csv") as mock:
        yield mock


@pytest.fixture
def mock_retry():
    with patch.object(run_import_job, "retry") as mock:
        mock.side_effect = Retry("retry called")
        yield mock


def test_run_import_job_success(mock_session_local, mock_process_csv):
    run_import_job.run(1, "fakefile.csv")
    mock_process_csv.assert_called_once_with(
        "fakefile.csv", 1, mock_session_local
    )


def test_run_import_job_failure_retry(
    mock_session_local,
    mock_process_csv,
    mock_retry,
):
    mock_process_csv.side_effect = Exception("fail")
    with pytest.raises(Retry):
        run_import_job.run(1, "fakefile.csv")
    mock_retry.assert_called_once()
