from typing import *

from inflection import underscore
from pydantic import validator

__all__ = ['snaky', 'parsed_group', 'parsed_match']

T = TypeVar('T', Dict[str, 'T'], List['T'], str, int, float, type(None))


def snaky_str(datum: str) -> str:
    return underscore(datum)  # camel_case_name


def snaky_dict(datum: Dict[str, T]) -> Dict[str, T]:
    return {snaky_str(k): snaky(v) for k, v in datum.items()}


def snaky_list(datum: List[T]) -> List[T]:
    return [snaky(d) for d in datum]


def snaky(datum: T) -> T:
    if isinstance(datum, dict):
        return snaky_dict(datum)
    if isinstance(datum, list):
        return snaky_list(datum)
    return datum


def parsed_group(func, group=None):
    if group is None:
        group = func

    @validator(func, pre=True, always=True, allow_reuse=True)
    def parse(cls, v, values, **kwargs):
        if v is not None:
            return v
        parsed_description = values.get('parsed_description')
        if parsed_description is None:
            raise ValueError("not parsed")
        return parsed_description.group(group)

    return parse


def parsed_match(field, group=None, translate=lambda x: x):
    if group is None:
        group = field

    @validator(field, allow_reuse=True)
    def match(cls, v, values, **kwargs):
        # use assert to be optimized
        assert 'parsed_description' not in values or \
               values['parsed_description'] is None or \
               v == translate(values['parsed_description'].group(group)), f'{field} do not match'
        return v

    return match
