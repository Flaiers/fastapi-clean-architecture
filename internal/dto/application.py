from pydantic import BaseModel, EmailStr

from internal.usecase.utils import PhoneStr


class BaseApplication(BaseModel):

    phone: PhoneStr
    email: EmailStr
    text: str


class ApplicationRead(BaseApplication):

    id: int

    class Config(object):
        orm_mode = True
