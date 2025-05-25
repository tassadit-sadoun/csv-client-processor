from uuid import UUID
from pydantic import BaseModel


class ImportJobResponse(BaseModel):
    job_id: UUID
    status: str

    class Config:
        from_attributes = True
