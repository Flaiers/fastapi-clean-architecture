from asyncio import AbstractEventLoop
from typing import Type

import aio_pika

from pkg.rabbitmq.rpc import RPCRouter
from pkg.rabbitmq.rpc.types import JsonRPC, UnionRPC


class RPCServer(object):

    def __init__(
        self,
        url: str,
        rpc: Type[UnionRPC] = JsonRPC,
    ) -> None:
        self.url = url
        self.RPC = rpc
        self.router = RPCRouter()
        self.loop: AbstractEventLoop | None = None

    def set_event_loop(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    def include_router(self, router: RPCRouter, *, prefix: str = '') -> None:
        self.router.include_router(router, prefix=prefix)

    async def connect(self) -> None:
        connection = await aio_pika.connect_robust(
            self.url, loop=self.loop, client_properties={
                'connection_name': 'Read connection',
            },
        )
        channel = await connection.channel()
        rpc = await self.RPC.create(channel)

        for route in self.router.routes:
            await rpc.register(
                route['path'].lstrip('_'),
                route['endpoint'],
                **route['kwargs'],
            )
