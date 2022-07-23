from typing import Dict

from pkg.rabbitmq.rpc import RPCRouter

router = RPCRouter()


@router.procedure('/metrics', durable=True, auto_delete=True)
async def read_metrics(
    *, datetime_from: str = '', datetime_to: str = '',
) -> Dict[str, int]:
    return {}
