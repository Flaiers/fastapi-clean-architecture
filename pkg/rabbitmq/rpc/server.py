from typing import Type

import aio_pika
from aio_pika.patterns import RPC, JsonRPC

from pkg.rabbitmq.rpc import RPCRouter


class RPCServer(object):

    def __init__(self, url, rpc: Type[RPC] | Type[JsonRPC] = RPC) -> None:
        self.url = url
        self.RPC = rpc
        self.router = RPCRouter()

    def set_event_loop(self, loop) -> None:
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
