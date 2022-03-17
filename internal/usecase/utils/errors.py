from pydantic.errors import PydanticValueError


class PhoneError(PydanticValueError):

    code = 'phone'
    msg_template = '"{phone}" is not a valid phone number'
