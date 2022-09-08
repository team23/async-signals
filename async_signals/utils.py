import functools
import inspect
from typing import Callable, Tuple

# Those functions are copied from
# https://github.com/django/django/blob/main/django/utils/inspect.py


@functools.lru_cache(maxsize=512)
def _get_func_parameters(
    func: Callable,
    remove_first: bool,
) -> Tuple[inspect.Parameter, ...]:
    parameters = tuple(inspect.signature(func).parameters.values())
    if remove_first:
        parameters = parameters[1:]
    return parameters


def _get_callable_parameters(
    meth_or_func: Callable,
) -> Tuple[inspect.Parameter, ...]:
    is_method = inspect.ismethod(meth_or_func)
    func = meth_or_func.__func__ if is_method else meth_or_func
    return _get_func_parameters(func, remove_first=is_method)


def func_accepts_kwargs(func: Callable) -> bool:
    """Return True if function 'func' accepts keyword arguments **kwargs."""

    return any(p for p in _get_callable_parameters(func) if p.kind == p.VAR_KEYWORD)
