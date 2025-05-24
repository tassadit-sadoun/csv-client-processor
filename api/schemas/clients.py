from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class ClientSchema(BaseModel):
    name: str
    email: EmailStr
    birth_date: Optional[date]


class ClientResponse(BaseModel):
    id: int
    name: str
    email: str
    birth_date: date

    class Config:
        from_attributes = True


class PaginatedClientsResponse(BaseModel):
    clients: List[ClientResponse]
    page: int
    total_pages: int
