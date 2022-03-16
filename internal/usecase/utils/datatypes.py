from typing import Any, Callable, ClassVar, Dict, Generator

from pydantic.fields import FieldInfo, ModelField

from internal.usecase.utils import validators

CallableGenerator = Generator[Callable[..., Any], None, None]


class PhoneStr(str):

    type: ClassVar[str] = "string"
    format: ClassVar[str] = "phone"
    example: ClassVar[str] = "+78005553535"
    pattern: ClassVar[str] = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"

    min_length: ClassVar[int] = 9
    max_length: ClassVar[int] = 15

    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield cls.validate

    @classmethod
    def validate(cls, value: str, field: ModelField) -> str:
        return validators.validate_phone(value)

    @classmethod
    def __modify_schema__(
        cls, field_schema: Dict[str, Any], field: ModelField | None
    ) -> None:
        field_info = FieldInfo(
            ...,
            regex=cls.pattern,
            example=cls.example,
            min_length=cls.min_length,
            max_length=cls.max_length,
        )
        field.field_info = field_info
        field_schema.update(
            type=cls.type,
            format=cls.format,
            example=cls.example,
            pattern=cls.pattern,
            minLength=cls.min_length,
            maxLength=cls.max_length,
        )
