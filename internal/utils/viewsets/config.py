from pydantic import BaseModel


__all__ = ["BaseConfig"]


class BaseConfig:

    include: set = set()
    exclude: set = set()
    filter_schema: BaseModel = BaseModel()
    update_schema: BaseModel = BaseModel()
    create_schema: BaseModel = BaseModel()
