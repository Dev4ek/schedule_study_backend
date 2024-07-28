from fastapi import HTTPException, Header, status, Security
from fastapi.security import OAuth2PasswordBearer
import os
from . import config
from icecream import ic
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=os.getenv('token'))

def verify_version(
        client_version: str = Header(..., description="Версия приложения у клиента", example="1.0.0")
        ):

    if client_version != config.version:
        raise HTTPException(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            detail="Version need upgrade",
        )

