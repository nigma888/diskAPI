from sqlalchemy import Column, Integer, String, DateTime, Enum, func

from externals.fileType import SystemItemType

from .database import Base


class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, index=True)
    type = Column(Enum(SystemItemType))
    date = Column(DateTime(timezone=True))
    url = Column(String, nullable=True)
    parentId = Column(String, nullable=True, index=True)
    size = Column(Integer, nullable=True)
