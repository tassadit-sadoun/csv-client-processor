from uuid import UUID
from typing import Literal

from pydantic import BaseModel


class ImportJobStatusResponse(BaseModel):
    job_id: UUID
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"]
    total: int
    valid: int
    errors: int
