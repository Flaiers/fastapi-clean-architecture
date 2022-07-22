import aio_pika
from aio_pika.patterns import RPC
from fastapi.datastructures import State


class RPCClient(object):

    def __init__(self, url: str, state: State) -> None:
        self.url = url
        self.state = state

    def set_event_loop(self, loop) -> None:
        self.loop = loop

    async def connect(self) -> RPC:
        connection = await aio_pika.connect_robust(
            self.url, loop=self.loop, client_properties={
                'connection_name': 'Write connection',
            },
        )
        channel = await connection.channel()
        return await RPC.create(channel)
