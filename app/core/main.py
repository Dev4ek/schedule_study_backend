import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import routers
from . import config
from loguru import logger
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from redis import asyncio as aioredis
import os
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title=config.APPname,
    version=config.version,
    docs_url='/docs', 
    openapi_url='/openapi.json',
    swagger_ui_parameters={"operationsSorter": "method"}
)

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_methods = ["*"],
  allow_credentials=True,
  allow_headers = ["*"]
)


app.include_router(routers.lesson.router_lesson)
app.include_router(routers.replace.router_replace)
app.include_router(routers.time.router_time)
app.include_router(routers.group.router_group)
app.include_router(routers.teacher.router_teacher)
app.include_router(routers.cabinet.router_cabinet)
app.include_router(routers.file.router_file)
app.include_router(routers.app.router_app)


@app.middleware("http")
async def maintenance_mode_middleware(request, call_next):
    if config.MAINTENANCE_MODE:
        return JSONResponse(
            status_code=503, 
            content={"message": "Сервер временно недоступен. Идут технические работы."}
        )
    response = await call_next(request)
    return response


async def start():
    import os   
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    import sys
    sys.dont_write_bytecode = True

    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == '__pycache__':
                full_path = os.path.join(root, d)
                os.system(f'rm -rf {full_path}')
                

    Instrumentator().instrument(app).expose(app) # prometheus metrics


    config = uvicorn.Config("app.core.main:app", host='0.0.0.0', port=8082, workers=1)
    server = uvicorn.Server(config)
 
    logger.info("Server FastAPI started")
    await server.serve()


