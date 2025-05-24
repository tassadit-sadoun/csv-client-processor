from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from crud import import_job_crud
from database.db import db_context
from log_config.log import get_logger
from schemas.status import ImportJobStatusResponse

log = get_logger(__name__)


router = APIRouter()


@router.get(
    "/{job_id}/status",
    response_model=ImportJobStatusResponse,
    status_code=status.HTTP_200_OK,
)
def get_import_status(job_id: UUID, db=Depends(db_context)):
    job = import_job_crud.get_one(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    row_stats = job.row_stats or {"total": 0, "valid": 0, "errors": 0}
    return ImportJobStatusResponse(
        job_id=job.id,
        status=job.status.name.upper(),
        total=row_stats.get("total", 0),
        valid=row_stats.get("valid", 0),
        errors=row_stats.get("errors", 0),
    )
