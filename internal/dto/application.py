from pydantic import BaseModel, EmailStr, Field, validator

from internal.usecase import errors


__all__ = ["BaseApplication", "ApplicationRead"]


class BaseApplication(BaseModel):

    phone: str = Field(max_length=255)
    email: EmailStr
    text: str

    @validator("phone")
    def validate_phone(cls, v: str):
        if not v.startswith(("+7", "8")) or \
               len(v.replace("+", "")) != 11:
            raise errors.PhoneError()
        return v


class ApplicationRead(BaseApplication):

    id: int

    class Config:
        orm_mode = True
