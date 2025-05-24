from sqlalchemy import Column, Integer, String, Date
from database.base_class import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    birth_date = Column(Date, index=True, nullable=False)
