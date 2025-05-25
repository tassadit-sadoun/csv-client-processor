from typing import List, Optional, Type

from sqlalchemy.orm import Session

from log_config.log import get_logger

log = get_logger(__name__)


class CRRepository:
    """
    Generic base class for basic Create and Read
    operations on a SQLAlchemy model.

    This repository provides:
    - `create`: Insert a new record into the database.
    - `get_one`: Retrieve a single record by its ID.
    - `get_many`: Retrieve multiple records with pagination support.
    """

    def __init__(self, model: Type):
        self.model = model

    def get_one(self, db: Session, id: int) -> Optional[object]:
        try:
            record = db.query(self.model).get(id)
            log.debug(
                f"Retrieved {self.model.__name__} with ID={id}"
            )
            return record
        except Exception as e:
            log.error(
                f"Error retrieving {self.model.__name__} with "
                f"ID={id}: {e}",
                exc_info=True,
            )

            return None

    def get_many(self, db: Session, skip: int = 0, limit: int = 10) -> List:
        try:
            records = db.query(self.model).offset(skip).limit(limit).all()
            log.debug(
                f"Retrieved {len(records)} "
                f" {self.model.__name__}(s)"
                f"(skip={skip}, limit={limit})"
            )
            return records
        except Exception as e:
            log.error(
                f"Error retrieving many {self.model.__name__}: {e}",
                exc_info=True,
            )
            return []

    def create(self, db: Session, obj_in) -> object:
        try:
            db_obj = self.model(**obj_in.dict())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            log.info(
                f"Created new {self.model.__name__} "
                f"with ID={db_obj.id}"
            )
            return db_obj
        except Exception as e:
            db.rollback()
            log.error(
                f"Failed to create {self.model.__name__}: {e}",
                exc_info=True
            )
            raise
