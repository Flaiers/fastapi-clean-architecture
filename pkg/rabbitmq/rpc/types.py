from typing import Union

from aio_pika.patterns import RPC, JsonRPC

UnionRPC = Union[RPC, JsonRPC]
