from typing import Any, Callable

from fastapi import params

from .repository import Repository


def Inject(  # noqa: N802
    model: Callable[..., Any], *, use_cache: bool = True
) -> Any:
    class_name = "{0.__name__}{1.__name__}".format(model, Repository)
    class_bases = (Repository,)
    class_namespace = {"model": model}
    dependency = type(class_name, class_bases, class_namespace)
    return params.Depends(dependency=dependency, use_cache=use_cache)
