from typing import Any, Callable, Optional

from .repository import Repository


def Inject(dependency: Optional[Callable[..., Any]] = None):  # noqa: N802
    class_name = "{0.__name__}{1.__name__}".format(dependency, Repository)
    class_bases = (Repository,)
    class_namespace = {"model": dependency}
    return type(class_name, class_bases, class_namespace)
