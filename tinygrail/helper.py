from typing import *
from inflection import underscore

__all__ = ['snaky']

T = TypeVar('T', Dict[str, 'T'], List['T'], str, int, float, type(None))


def snaky_str(datum: str) -> str:
    return underscore(datum)  # camel_case_name


def snaky_dict(datum: Dict[str, T]) -> Dict[str, T]:
    return {snaky_str(k): snaky(v) for k, v in datum.items()}


def snaky_list(datum: List[T]) -> List[T]:
    return [snaky(d) for d in datum]


def snaky(datum: T) -> T:
    if isinstance(datum, str):
        return snaky_str(datum)
    if isinstance(datum, dict):
        return snaky_dict(datum)
    if isinstance(datum, list):
        return snaky_list(datum)
    return datum
