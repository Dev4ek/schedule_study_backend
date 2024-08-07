from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from .. import utils
from loguru import logger
from app.core.dependencies import SessionDep

router_group = APIRouter(prefix="/practice", tags=["Практика"])

@router_group.get(
        path="/all",
        summary="Список всех групп у которых идет сейчас практика",
)
async def get_groups(
    session: SessionDep # Сессия базы даныых
) -> JSONResponse:
    logger.info("Запрос на получение списка всех групп")

    getting = await utils.all_groups(session)

    if getting:
        logger.info("Отдаём ответ сформированный список")
        return JSONResponse(content=getting, status_code=200)
    else:
        logger.error("Неизвестная ошибка при получении списка всех групп. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при получении списка групп"}, status_code=500)
    

@router_group.put(
        path="/put/{group}",
        summary="Добавить группу",
      
)
async def put_group(
    session: SessionDep, # Сессия базы даных
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на вставку группы. Группа: {group}")

    adding: bool | str = await utils.put_group(group, session)

    if adding == "exists":
        logger.info("Группа уже существует. Отдаём ответ")
        return JSONResponse(content={"message": "Группа уже существует"}, status_code=409)

    elif adding:
        logger.info("Группа успешно добавлена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа успешно добавлена"}, status_code=200)

    else:
        logger.error("Неизвестная ошибка при добавлении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении группы"}, status_code=500)
    


@router_group.delete(
        path="/remove/{group}",
        summary="Удалить группу",
       
)
async def remove_group(
    session: SessionDep, # Сессия базы даных
    group: str = Path(..., description="Группа", example="Исп-232")
) -> JSONResponse:
    logger.info(f"Запрос на удаление группы. Группа: {group}")

    removing: bool | str = await utils.remove_group(group, session)

    if removing == "not found":
        logger.info("Группа не найдена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа не найдена"}, status_code=404)
    
    elif removing:
        logger.info("Группа успешно удалена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа успешно удалена"}, status_code=200)
    
    else:
        logger.error("Ошибка при удалении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка удалении группы"}, status_code=500)
    
