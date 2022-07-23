import asyncio

from internal.config.database import create_database
from pkg.rabbitmq.rpc import RPCClient, RPCServer


def startup_database(url: str):
    async def wrapper():
        await create_database(url)

    return wrapper


def startup_rpc_server(rpc: RPCServer):
    async def wrapper():
        loop = asyncio.get_event_loop()
        rpc.set_event_loop(loop)
        asyncio.ensure_future(rpc.connect())

    return wrapper


def startup_rpc_client(rpc: RPCClient):
    async def wrapper():
        loop = asyncio.get_event_loop()
        rpc.set_event_loop(loop)
        rpc.state.rpc = await rpc.connect()

    return wrapper


def shutdown_rpc_client(rpc: RPCClient):
    async def wrapper():
        await rpc.state.rpc.close()

    return wrapper
