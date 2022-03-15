from .base import BaseRepository  # noqa: WPS300


class InjectRepository(object):

    def __init__(self, model) -> None:
        self.model = model

    def __call__(self, *args, **kwargs):
        class Repository(BaseRepository):  # noqa: WPS431

            model = self.model

        return Repository
