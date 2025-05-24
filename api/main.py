from fastapi import FastAPI

from routers import clients_router, imports_router, status_router

import logging.config
from log_config.logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)


app = FastAPI(title="Client Data Ingestor", version="0.1.0")

app.include_router(imports_router)
app.include_router(status_router, prefix="/api/imports", tags=["imports"])
app.include_router(clients_router, prefix="/api/clients", tags=["clients"])
