import os
import logging.config

from celery import Celery
from sqlalchemy.exc import SQLAlchemyError

from database.db import SessionLocal
from log_config.logging_config import LOGGING_CONFIG
from log_config.log import get_logger
from services.import_service import process_csv

logging.config.dictConfig(LOGGING_CONFIG)

log = get_logger(__name__)


BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

app = Celery("tasks", broker=BROKER_URL, backend=RESULT_BACKEND)


@app.task(
    bind=True,
    autoretry_for=(SQLAlchemyError, IOError, Exception),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def run_import_job(self, job_id: int, filepath: str) -> None:
    log.info("Starting import job %d with file: %s", job_id, filepath)

    try:
        with SessionLocal() as db:
            process_csv(filepath, job_id, db)
        log.info("Import job %d completed successfully.", job_id)

    except Exception as e:
        log.error(
            "Import job %d failed. Error: %s", job_id, str(e),
            exc_info=True
        )
        raise self.retry(exc=e)
