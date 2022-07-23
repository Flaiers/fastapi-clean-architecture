from typing import Type, Union

from aio_pika.patterns import RPC, JsonRPC

UnionRPC = Union[Type[RPC], Type[JsonRPC]]
