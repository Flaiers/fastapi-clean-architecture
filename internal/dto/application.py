import uuid
from dataclasses import dataclass

from fastapi import Query
from pydantic import BaseModel, EmailStr

from internal.usecase.pydantic import PhoneStr


class BaseApplication(BaseModel):

    phone: PhoneStr
    email: EmailStr
    text: str


class ApplicationRead(BaseApplication):

    id: uuid.UUID

    class Config(object):
        orm_mode = True


@dataclass
class ApplicationFilter(object):

    phone: str = Query('')
    email: str = Query('')
