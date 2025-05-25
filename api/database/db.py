from typing import Generator

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from log_config.log import get_logger

POSTGRES_URL = os.getenv("POSTGRES_URL")

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)

log = get_logger(__name__)


def db_context() -> Generator:
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        log.error(
            "An error occurred while getting the database session. Error: "
            " %s", e
        )
        raise
    finally:
        log.debug("closing database session")
        session.close()
