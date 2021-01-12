from typing import Optional, Union, Literal, Tuple, Callable, List, Dict, ClassVar, ChainMap, Iterable


def parse_target(targets: Iterable[str]) -> Dict[int, Tuple[int, int]]: ...


class Target:
    tower_min: Optional[int]
    tower_max: Optional[int]
    holding_min: Optional[int]
    holding_max: Optional[int]

    def __init__(self, holding_min=None, holding_max=None, tower_min=None, tower_max=None): ...

    @classmethod
    def clone(cls, clones: Target) -> Target: ...

    def check(self, holding: int, tower: int) -> Union[Literal['sacrifice'],
                                                       Tuple[Literal['match',
                                                                     'high',
                                                                     'low',
                                                                     'confused target']]]: ...

    def colored_comparison(self, holding: int, tower: int) -> str: ...

    def load_from_rhs(self, rhs: str): ...


_Resolver = Callable[[str], List[int]]


class Targets(Dict[str, Target]):
    _class_resolver: ClassVar[Dict[str, _Resolver]]
    resolver: ChainMap[str, _Resolver]

    def load_line(self, line: str): ...

    def load_lines(self, lines: Iterable[str]): ...

    @classmethod
    def add_class_resolver(cls, *prefixes) -> Callable[[_Resolver], None]: ...

    def add_resolver(self, *prefixes: str) -> Callable[[_Resolver], None]: ...

    def init_macros(self): ...

    def cleanup_macros(self): ...
