from sqlalchemy.orm import Session

from models import Client

from .base import CRRepository


class CRRClient(CRRepository):
    def __init__(self):
        super().__init__(Client)

    def get_paginated(self, db: Session, skip: int, limit: int) -> dict:
        query = db.query(self.model).order_by(self.model.id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return {"total": total, "skip": skip, "limit": limit, "items": items}


client_crud = CRRClient()
