from .base import BaseRepository  # noqa: WPS300


class InjectRepository(object):

    def __init__(self, model):
        self.model = model

    def __call__(self):
        class Repository(BaseRepository):

            model = self.model

        return Repository
