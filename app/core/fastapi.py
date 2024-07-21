import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import routers
from . import config
from loguru import logger


app = FastAPI(
    title=config.APPname,
    version=config.version,
    docs_url='/docs', 
    openapi_url='/openapi.json'
)

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_methods = ["*"],
  allow_credentials=True,
  allow_headers = ["*"]
)


app.include_router(routers.schedule.router)
app.include_router(routers.time.router)


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
                

    # asyncio.run(core.drop_tables())
    # asyncio.run(core.create_tables())

    # Instrumentator().instrument(app).expose(app) # prometheus metrics


    config = uvicorn.Config("app.core.fastapi:app", host='0.0.0.0', port=8082, workers=1)
    server = uvicorn.Server(config)
 
    logger.info("Server FastAPI started")
    await server.serve()


