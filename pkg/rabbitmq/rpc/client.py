from asyncio import AbstractEventLoop
from typing import Type

import aio_pika
from fastapi.datastructures import State

from pkg.rabbitmq.rpc.types import JsonRPC, UnionRPC


class RPCClient(object):

    def __init__(
        self,
        url: str,
        state: State,
        rpc: Type[UnionRPC] = JsonRPC,
    ) -> None:
        self.url = url
        self.RPC = rpc
        self.state = state
        self.loop: AbstractEventLoop | None = None

    def set_event_loop(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    async def connect(self, **kwargs) -> UnionRPC:
        connection = await aio_pika.connect_robust(
            self.url, loop=self.loop, client_properties={
                'connection_name': 'Write connection',
            },
        )
        channel = await connection.channel()
        return await self.RPC.create(channel, **kwargs)
