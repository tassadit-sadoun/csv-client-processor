import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, JSON, func
from sqlalchemy.dialects.postgresql import UUID

from database.base_class import Base


class JobStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    row_stats = Column(
        JSON, nullable=False, default=lambda:
        {"total": 0, "valid": 0, "errors": 0}
    )
