from pydantic import Field, BaseModel, validator, ValidationError
from typing import Optional, List
from datetime import datetime


from externals.fileType import SystemItemType


class SystemItemBase(BaseModel):
    id: str = Field(description="Уникальный идентфикатор")
    type: SystemItemType = Field(description="Тип элемента - папка или файл")


class SystemItem(SystemItemBase):
    url: Optional[str] = Field(
        default=None, description="Ссылка на файл. Для папок поле равнно null."
    )
    date: datetime = Field(description="Время последнего обновления элемента.")
    parentId: Optional[str] = Field(default=None, description="id родительской папки")
    size: Optional[int] = Field(
        default=None,
        description="Целое число, для папки - это суммарный размер всех элеметов.",
    )
    children: Optional[List["SystemItem"]] = Field(
        default=None,
        description="Список всех дочерних элементов. Для файлов поле равно null.",
    )

    @validator("date")
    def correct_format(cls, v):
        return v.strftime("%Y-%m-%dT%H:%M:%SZ")

    class Config:
        orm_mode = True


class SystemItemImport(SystemItemBase):
    url: Optional[str] = Field(
        default=None, description="Ссылка на файл. Для папок поле равнно null."
    )
    parentId: Optional[str] = Field(default=None, description="id родительской папки")
    size: Optional[int] = Field(
        default=None,
        description="Целое число, для папки - это суммарный размер всех элеметов.",
    )

    @validator("url")
    def folder_without_url(cls, v, values):
        if values["type"] == "FOLDER" and v:
            raise ValidationError("1")
        elif len(v) > 255:
            raise ValidationError("2")
        return v

    @validator("size")
    def folder_without_size(cls, v, values):
        if values["type"] == "FOLDER" and v:
            raise ValidationError("3")
        elif v <= 0:
            raise ValidationError("4")
        return v


class SystemItemImportRequest(BaseModel):
    items: List[SystemItemImport] = Field(description="Импортируемые элементы")
    updateDate: datetime = Field(description="Время обновления добавляемых элементов.")


class SystemItemHistoryUnit(SystemItemBase):
    url: Optional[str] = Field(
        default=None, description="Ссылка на файл. Для папок поле равнно null."
    )
    date: datetime = Field(description="Время последнего обновления элемента.")
    parentId: Optional[str] = Field(default=None, description="id родительской папки")
    size: Optional[int] = Field(
        default=None,
        description="Целое число, для папки - это суммарный размер всех элеметов.",
    )

    class Config:
        orm_mode = True


class SystemItemHistoryResponse(BaseModel):
    items: List[SystemItemHistoryUnit] = Field(
        description="История в произвольном порядке."
    )

    class Config:
        orm_mode = True


class Error(BaseModel):
    code: int = Field()
    message: str = Field()
