from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from .. import schemas

from db.models import Item

from db.crud import get_updated_nodes, add_item
from db import crud


class ExceptionWithMessage(Exception):
    def __init__(self, message: str, code: int):
        self.message = message
        self.code = code


async def imports(
    request: schemas.SystemItemImportRequest,
    session: AsyncSession,
):
    parents_ids = []
    idies = set()
    for i in request["items"]:
        if i["id"] in idies:
            raise ExceptionWithMessage("Validation Failed", 400)
        if i["parentId"]:
            parent = await crud.get_node_by_id(i["parentId"], session)
            if not parent or parent.type != "FOLDER":
                raise ExceptionWithMessage("Validation Failed", 400)
            parents_ids.append(i["parentId"])
        idies.add(i["id"])
        item = await crud.get_node_by_id(i["id"], session)
        if item:
            item.url = i["url"]
            item.date = request["updateDate"]
            item.type = i["type"]
            item.parentId = i["parentId"]
            item.size = i["size"]
            session.add(item)
        else:
            add_item(request["updateDate"], i, session)
    await update_date_for_all_parent(parents_ids, request["updateDate"], session)

    await session.commit()


async def update_date_for_all_parent(parents, date, session: AsyncSession):
    new_parent = []
    for i in parents:
        item = await crud.get_node_by_id(i, session)
        item.date = date
        session.add(item)
        if item.parentId:
            new_parent.append(item.parentId)
    if new_parent:
        await update_date_for_all_parent(new_parent, date, session)


async def delete_by_id(id: str, session: AsyncSession):
    await delete_with_child(id, session)
    await session.commit()


async def delete_with_child(id: str, session: AsyncSession):
    item = await crud.get_node_by_id(id, session)
    if not item:
        raise ExceptionWithMessage("Item not found", 404)
    item = jsonable_encoder(item)
    if item["type"] == "FILE":
        return await crud.delete_by_id(item["id"], session)
    item["children"] = await crud.get_children(item["id"], session)
    for i in range(len(item["children"])):
        await delete_with_child(item["children"][i].id, session)
    await crud.delete_by_id(item["id"], session)


async def fill_child(item, session: AsyncSession):
    item = jsonable_encoder(item)
    if item["type"] == "FILE":
        return item
    item["children"] = await crud.get_children(item["id"], session)
    for i in range(len(item["children"])):
        item["children"][i] = await fill_child(item["children"][i], session)
    return item


def calculate_size(item):
    if item["type"] == "FILE":
        return item["size"]
    item["size"] = 0
    for i in range(len(item["children"])):
        item["size"] += calculate_size(item["children"][i])
    return item["size"]


async def get_node_by_id(id: str, session: AsyncSession):
    item = await crud.get_node_by_id(id, session)
    if not item:
        raise ExceptionWithMessage("Item not found", 404)

    item = await fill_child(item, session)
    if item["type"] == "FOLDER":
        item["size"] = calculate_size(item)

    return item


async def updates(date, session: AsyncSession):
    items = await get_updated_nodes(date, session)
    return {"items": items}
