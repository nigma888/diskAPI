import enum


class SystemItemType(str, enum.Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"
