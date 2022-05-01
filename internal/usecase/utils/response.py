from internal.usecase.utils import response_schema

RESPONSE_401_UNAUTHORIZED = response_schema(
    example={'successful': False, 'detail': 'Unauthorized'},
    description='Unauthorized',
    status_code=401,
)

RESPONSE_403_FORBIDDEN = response_schema(
    example={'successful': False, 'detail': 'Forbidden'},
    description='Forbidden',
    status_code=403,
)

RESPONSE_404_NOT_FOUND = response_schema(
    example={'successful': False, 'detail': 'Not found'},
    description='Not found',
    status_code=404,
)
