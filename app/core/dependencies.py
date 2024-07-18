from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
import os
from icecream import ic
from . import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=os.getenv('token'))

def verify_version(
        client_version: str = Header(...)
        ):
    
    if client_version != config.version:
        raise HTTPException(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            detail="Version is outdated",
        )


