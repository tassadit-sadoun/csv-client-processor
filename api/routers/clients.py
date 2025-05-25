from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from crud import client_crud
from database.db import db_context
from log_config.log import get_logger
from schemas.clients import ClientResponse, PaginatedClientsResponse
from security.auth.token_utils import verify_token
router = APIRouter()

log = get_logger(__name__)


@router.get(
    "",
    response_model=PaginatedClientsResponse,
    status_code=status.HTTP_200_OK
)
def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1),
    db: Session = Depends(db_context),
    payload: dict = Depends(verify_token)
):
    log.info(
        "Received request to list clients (page=%d, per_page=%d)",
        page, per_page
    )

    try:
        pagination_result = client_crud.get_paginated(
            db, skip=(page - 1) * per_page, limit=per_page)

        if not pagination_result or "items" not in pagination_result:
            log.error("Invalid pagination result from client_crud")
            raise HTTPException(status_code=500, 
                                detail="Failed to retrieve clients")

        clients = pagination_result["items"]
        total_clients = pagination_result["total"]
        total_pages = (total_clients + per_page - 1) // per_page

        log.debug(
            "Total clients found: %d, returning page %d/%d",
            total_clients,
            page,
            total_pages,
        )

        return PaginatedClientsResponse(
            clients=[ClientResponse.from_orm(client) for client in clients],
            page=page,
            total_pages=total_pages,
        )

    except Exception as e:
        log.error("Failed to list clients: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
