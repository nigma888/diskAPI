from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from fastapi.encoders import jsonable_encoder


from datetime import timedelta

from .database import get_session

from .models import Item


async def get_node_by_id(id, session: AsyncSession):
    result = await session.execute(select(Item).where(Item.id == id))
    return result.scalars().first()


async def get_updated_nodes(date, session: AsyncSession):
    items = await session.execute(
        select(Item).where(Item.date.between(date - timedelta(days=1), date))
    )
    return items.scalars().all()


def add_item(date, item, session: AsyncSession):
    item = Item(date=date, **item)
    session.add(item)


async def get_children(id, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Item).where(Item.parentId == id))
    return res.scalars().all()


async def delete_by_id(id, session: AsyncSession):
    item = await session.execute(select(Item).where(Item.id == id))
    item = item.scalars().first()
    await session.delete(item)
