from fastapi import Request


def get_rpc(request: Request):
    return request.app.state.rpc
