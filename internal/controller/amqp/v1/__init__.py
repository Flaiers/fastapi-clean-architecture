from pkg.rabbitmq.rpc import RPCRouter

from . import applications

router = RPCRouter()
router.include_router(
    applications.router,
    prefix='/applications',
)
