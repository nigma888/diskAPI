from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

from .. import schemas

from db.database import get_session

from ..handlers import files

router = APIRouter(tags=["files"])


@router.post(
    "/imports",
    description="Импортирует элементы файловой системы. Элементы импортированные повторно обновляют текущие."
    "Изменение типа элемента с папки на файл и с файла на папку не допускается."
    "Порядок элементов в запросе является произвольным.",
)
async def imports(
    request: schemas.SystemItemImportRequest,
    session: AsyncSession = Depends(get_session),
):
    return await files.imports(request.dict(), session)


@router.delete(
    "/delete/{id}",
    description="Удалить элемент по идентификатору. При удалении папки удаляются все дочерние элементы."
    "Доступ к истории обновлений удаленного элемента невозможен.",
)
async def delete_by_id(id: str, session: AsyncSession = Depends(get_session)):
    return await files.delete_by_id(id, session)


@router.get(
    "/nodes/{id}",
    response_model=schemas.SystemItem,
    description="""Получить информацию об элементе по идентификатору. При получении информации о папке также предоставляется информация о её дочерних элементах.

        - для пустой папки поле children равно пустому массиву, а для файла равно null
        - размер папки - это суммарный размер всех её элементов. Если папка не содержит элементов, то размер равен 0. При обновлении размера элемента, суммарный размер папки, которая содержит этот элемент, тоже обновляется.""",
)
async def get_node_by_id(id: str, session: AsyncSession = Depends(get_session)):
    return await files.get_node_by_id(id, session)


@router.get(
    "/updates",
    response_model=schemas.SystemItemHistoryResponse,
    description="Получение списка **файлов**, которые были обновлены за последние 24"
    "аса включительно [date - 24h, date] от времени переданном в запросе.",
)
async def updates(date: datetime, session: AsyncSession = Depends(get_session)):
    return await files.updates(date, session)
