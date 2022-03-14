from pydantic import BaseModel


class BaseConfig(object):

    include: set = set()
    exclude: set = set()
    filter_schema: BaseModel = BaseModel
    update_schema: BaseModel = BaseModel
    create_schema: BaseModel = BaseModel
