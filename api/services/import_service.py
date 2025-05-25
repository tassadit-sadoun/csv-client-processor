from datetime import datetime

import pandas as pd
from pydantic import ValidationError
from sqlalchemy.orm import Session

from log_config.log import get_logger
from models import Client
from models import ImportJob, JobStatus
from schemas.clients import ClientSchema

log = get_logger(__name__)


def parse_date(date_str):
    try:
        if not date_str or pd.isna(date_str):
            return None
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        log.warning("Failed to parse date '%s': %s", date_str, e)
        return None


def process_csv(filepath: str, job_id: int, db: Session):
    job = db.query(ImportJob).get(job_id)
    job.status = JobStatus.in_progress
    db.commit()

    try:
        df = pd.read_csv(filepath, skipinitialspace=True)
    except Exception as e:
        log.error("Failed to read CSV file '%s': %s", filepath, e)
        job.status = JobStatus.failed
        db.commit()
        return

    total, valid, errors = 0, 0, 0

    for i, row in df.iterrows():
        total += 1
        try:
            client = ClientSchema(
                name=row["nom"],
                email=row["email"],
                birth_date=parse_date(row["date de naissance"]),
            )
            db.add(Client(**client.dict()))
            valid += 1
        except (ValidationError, ValueError) as e:
            errors += 1
            log.warning("Validation error at row %d: %s", i, e)

    job.row_stats = {"total": total, "valid": valid, "errors": errors}
    job.status = (
        JobStatus.completed
        if errors == 0
        else JobStatus.failed if valid == 0 else JobStatus.completed
    )
    db.commit()
