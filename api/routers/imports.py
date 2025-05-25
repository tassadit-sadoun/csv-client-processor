import os
import shutil

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from database.db import db_context
from models import ImportJob, JobStatus
from log_config.log import get_logger
from schemas.imports import ImportJobResponse
from tasks import run_import_job
from security.auth.token_utils import verify_token

router = APIRouter(prefix="/api/imports", tags=["imports"])

log = get_logger(__name__)


@router.post("", response_model=ImportJobResponse)
def import_clients(
    file: UploadFile = File(...),
    db: Session = Depends(db_context),
    _: dict = Depends(verify_token)
):
    shared_dir = "/shared_data"
    try:
        os.makedirs(shared_dir, exist_ok=True)
        temp_path = os.path.join(shared_dir, file.filename)
        log.info("Saving uploaded file to: %s", temp_path)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        log.error("Failed to save uploaded file: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file.",
        )

    try:
        job = ImportJob(status=JobStatus.pending)  # type: ignore
        db.add(job)
        db.commit()
        db.refresh(job)
        log.info("Created import job with ID %s", job.id)
    except Exception as e:
        db.rollback()
        log.error("Failed to create import job: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create import job.",
        )

    try:
        run_import_job.delay(job.id, temp_path)
        log.info("Dispatched import job %s with file %s", job.id, temp_path)
    except Exception as e:
        log.error("Failed to dispatch import job %s: %s", job.id, e,
                  exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start import job.",
        )

    return ImportJobResponse(job_id=job.id, status=job.status.value)
