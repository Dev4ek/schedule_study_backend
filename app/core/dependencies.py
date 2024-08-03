from fastapi import HTTPException, Header, status, Security, Depends
from fastapi.security import OAuth2PasswordBearer
import os
from . import config
from icecream import ic
from jose import jwt
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import database as db


SessionDep = Annotated[AsyncSession, Depends(db.get_session)]

def verify_version(
        client_version: str = Header(..., description="Версия приложения", example="1.0.0")
        ):
    
    if client_version != config.version:
        raise HTTPException(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            detail="Version need upgrade",
        )
    return True
