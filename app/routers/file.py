from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse, FileResponse
from .. import utils
from loguru import logger
from app.core.dependencies import SessionDep

router_file = APIRouter(prefix="/file", tags=["Файлы"])

@router_file.get(
        path="/raspisanie.xls",
        summary="Сформировать и скачать файл raspisanie.xls"
)
async def file_raspisanie(
    session: SessionDep # Сессия базы даныых
) -> JSONResponse:
    logger.info("Запрос на формирование и скачивание файла raspisanie.xls")

    getting = await utils.get_file_raspisanie(session)

    if getting:
        logger.info("Отдаём ответ файл")
        return FileResponse(path="raspisanie.xls", status_code=200)
    else:
        logger.error("Неизвестная ошибка при формировании файла. Оидаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при скачиваинии файла"}, status_code=500)
    

@router_file.get(
        path="/zameni.docx",
        summary="Сформировать и скачать файл zameni.docx",
)
async def file_zameni(
    session: SessionDep, # Сессия базы даных
) -> JSONResponse:
    logger.info(f"Запрос на формирование и скачивание файла zameni.docx")

    getting: bool | str = await utils.put_group(session)

    if getting:
        logger.info("Группа успешно добавлена. Отдаём ответ")
        return JSONResponse(content={"message": "Группа успешно добавлена"}, status_code=200)

    else:
        logger.error("Неизвестная ошибка при добавлении группы. Отдаём ответ")
        return JSONResponse(content={"message": "Неизвестная ошибка при добавлении группы"}, status_code=500)
    

