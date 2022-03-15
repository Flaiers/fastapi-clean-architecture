from .base import BaseRepository


class InjectRepository(object):

    def __init__(self, model):
        self.model = model

    def __call__(self, new_repository):
        return type(
            new_repository.__name__, (BaseRepository,), {"model": self.model}
        )
