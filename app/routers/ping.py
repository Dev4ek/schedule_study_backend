from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from ..core import dependencies

router = APIRouter()

@router.get(
        "/status", 
        tags=["Проверка"]
        )
async def get_status(
    auth: str = Depends(dependencies.verify_version),
    client_version: str = Header(..., description="Версия приложения")
    ):

    return JSONResponse(status_code=200, content={"status": "ok"})




