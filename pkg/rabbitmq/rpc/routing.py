from typing import Any, Callable, Dict, List


class RPCRouter(object):

    def __init__(self, *, prefix: str = '') -> None:
        if prefix:
            self.validate_prefix(prefix)

        self.prefix = prefix.replace('/', '_')
        self.routes: List[Dict[str, Any]] = []

    def validate_prefix(self, prefix: str) -> None:
        assert prefix.startswith('/'), 'A path prefix must start with "/"'
        assert not prefix.endswith('/'), 'A path prefix must not end with "/"'

    def add_rpc_route(self, path: str, endpoint: Callable[..., Any], **kwargs):
        self.routes.append({
            'path': path, 'endpoint': endpoint, 'kwargs': kwargs,
        })

    def rpc_route(self, path: str, **kwargs):
        def wrapper(endpoint: Callable[..., Any]):
            self.add_rpc_route(path, endpoint, **kwargs)
            return endpoint

        return wrapper

    def include_router(self, router: 'RPCRouter', *, prefix: str = '') -> None:
        if prefix:
            self.validate_prefix(prefix)

        for route in router.routes:
            path = prefix + route['path']
            self.add_rpc_route(
                path.replace('/', '_'),
                route['endpoint'],
                **route['kwargs'],
            )

    def procedure(
        self,
        path: str,
        *,
        durable: bool = False,
        exclusive: bool = False,
        passive: bool = False,
        auto_delete: bool = False,
    ):
        return self.rpc_route(
            path=path,
            durable=durable,
            exclusive=exclusive,
            passive=passive,
            auto_delete=auto_delete,
        )
