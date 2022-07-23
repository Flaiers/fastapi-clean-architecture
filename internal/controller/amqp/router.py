from internal.controller.amqp import v1
from pkg.rabbitmq.rpc import RPCRouter

rpc_router = RPCRouter()
rpc_router.include_router(v1.router, prefix='/v1')
