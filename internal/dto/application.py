from pydantic import BaseModel, EmailStr, validator

from internal.usecase.utils import validate_phone

__all__ = ["BaseApplication", "ApplicationRead"]


class BaseApplication(BaseModel):

    email: EmailStr
    phone: str
    text: str

    @validator("phone")
    def validate_phone(cls, v: str):  # noqa: N805
        return validate_phone(v)


class ApplicationRead(BaseApplication):

    id: int

    class Config:
        orm_mode = True
