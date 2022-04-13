from internal.usecase.utils import response_schema

RESPONSE_401_UNAUTHORIZED = response_schema(
    content={'detail': 'Unauthorized'},
    description='Unauthorized',
    status_code=401,
    editable=True,
)

RESPONSE_403_FORBIDDEN = response_schema(
    content={'detail': 'Forbidden'},
    description='Forbidden',
    status_code=403,
    editable=True,
)

RESPONSE_404_NOT_FOUND = response_schema(
    content={'detail': 'Not found'},
    description='Not found',
    status_code=404,
    editable=True,
)
