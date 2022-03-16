from typing import Any, Callable, Optional

from .repository import Repository  # noqa: WPS300


class Inject(object):

    def __init__(self, dependency: Optional[Callable[..., Any]] = None):
        self.dependency = dependency

    def __call__(self):
        class_name = "{0.__name__}{1.__name__}".format(
            self.dependency, Repository
        )
        class_bases = (Repository,)
        class_namespace = {"model": self.dependency}
        return type(class_name, class_bases, class_namespace)
