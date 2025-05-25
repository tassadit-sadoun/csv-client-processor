import os
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from security.auth.token_utils import (
    create_access_token,
    validate_client_credentials
    )
from log_config.log import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/access_token")
def access_token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    if grant_type != "client_credentials":
        raise HTTPException(status_code=400, detail="Unsupported grant_type")
    if not validate_client_credentials(client_id, client_secret):
        raise HTTPException(status_code=401,
                            detail="Invalid client credentials")

    token = create_access_token(client_id)
    log.info(f"Token generated for client_id={client_id}")
    return JSONResponse({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 3600))
    })
