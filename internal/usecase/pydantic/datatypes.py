import re
from typing import Any, Callable, ClassVar, Dict, Generator, Pattern

from pydantic.validators import constr_length_validator, str_validator

from ..pydantic.validators import validate_phone  # noqa: WPS300

CallableGenerator = Generator[Callable[..., Any], None, None]


class PhoneStr(str):  # noqa: WPS600

    example: ClassVar[str] = '+78005553535'
    regex: ClassVar[Pattern[str]] = re.compile(
        r'^(\+)[1-9][0-9\-().]{9,15}$',
    )
    min_length: ClassVar[int] = 9
    max_length: ClassVar[int] = 15

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield str_validator
        yield constr_length_validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(
            type='string',
            format='phone',
            example=cls.example,
            pattern=cls.regex.pattern,
            minLength=cls.min_length,
            maxLength=cls.max_length,
        )

    @classmethod
    def validate(cls, phone: str) -> str:
        return validate_phone(phone, cls.regex)
