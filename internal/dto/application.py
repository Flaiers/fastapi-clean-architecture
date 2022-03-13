from pydantic import BaseModel, EmailStr, Field, validator

from internal.usecase.utils import validate_phone


__all__ = ["BaseApplication", "ApplicationRead"]


class BaseApplication(BaseModel):

    phone: str = Field(max_length=255)
    email: EmailStr
    text: str

    @validator("phone")
    def validate_phone(cls, v: str):
        return validate_phone(v)


class ApplicationRead(BaseApplication):

    id: int

    class Config:
        orm_mode = True
