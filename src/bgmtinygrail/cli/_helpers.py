import re
from collections import ChainMap
from typing import Dict, Tuple

import click

__all__ = ['parse_target', 'Target', 'Targets']

from termcolor import colored

PARSER_RE = re.compile(r"(?:(?P<cid>\d+)|cv/(?P<cv_id>\d+)|(?:sub|subject)/(?P<sub_id>\d+))"
                       r" *= *"
                       r"(?P<hold>\d+)?(?:/(?P<tower>\d*))?")


def saturation(lb, v, rb):
    assert lb is None or rb is None or lb <= rb
    if v is None:
        v = lb
    if v is None:
        v = rb
    if lb is not None and v < lb:
        v = lb
    if rb is not None and v > rb:
        v = rb
    return v


def parse_target(targets):
    result: Dict[int, Tuple[int, int]] = {}
    for target in targets:
        t = PARSER_RE.fullmatch(target)
        if t is None:
            print(f"Bad target value `{target}`. Syntax: <cid> = <hold>/<tower>, cv/<cv_id> = <hold>/<tower>")
            raise click.exceptions.Exit(10)
        t = t.groupdict()
        requirement_of_this = int(t['hold'] or 0), int(t['tower'] or 0)
        if t['cid'] is not None:
            result[int(t['cid'])] = requirement_of_this
        elif t['cv_id'] is not None:
            from ..bgmd import person_work_voice_character, Person
            for cid in person_work_voice_character(Person(id=int(t['cv_id']))):
                result[cid.id] = requirement_of_this
        elif t['sub_id'] is not None:
            from ..bgmd.api import subject_character
            for cid in subject_character(int(t['sub_id'])):
                result[cid] = requirement_of_this
    return result


class Target:
    def __init__(self, holding_min=None, holding_max=None, tower_min=None, tower_max=None):
        self.tower_min = holding_min
        self.tower_max = holding_max
        self.holding_min = tower_min
        self.holding_max = tower_max

    @classmethod
    def clone(cls, clones):
        return cls(clones.holding_min, clones.holding_max, clones.tower_min, clones.tower_max)

    def __bool__(self):
        return (self.tower_min is not None or
                self.tower_max is not None or
                self.holding_min is not None or
                self.holding_max is not None)

    def __str__(self):
        def only_int(v):
            if v is None:
                return ""
            return str(v)

        def viz_range(lb, rb):
            if lb is None or rb is None or lb < rb:
                result = f"{only_int(lb)}-{only_int(rb)}"
                if result == "-":
                    result = ""
                return result
            elif lb == rb:
                return f"={lb}"
            else:
                return colored(f"{only_int(lb)}-{only_int(rb)}", on_color='on_red')

        sh = viz_range(self.holding_min, self.holding_max)
        st = viz_range(self.tower_min, self.tower_max)

        s = f"{sh}/{st}"
        if s == "/":
            s = ""
        return s

    def check(self, holding, tower):
        matrix = {
            (True, True): 'confused target',
            (True, False): 'low',
            (False, True): 'high',
            (False, False): 'match',
        }
        check_tower = matrix[(self.tower_min is not None and tower < self.tower_min,
                              self.tower_max is not None and tower > self.tower_max)]
        check_holding = matrix[(self.holding_min is not None and holding < self.holding_min,
                                self.holding_max is not None and holding > self.holding_max)]
        if check_tower == "low" and check_holding == "high" and holding + tower >= self.tower_min:
            return "sacrifice"
        else:
            return check_holding, check_tower

    def colored_comparison(self, holding, tower):
        check = self.check(holding, tower)
        colors = {
            'confused target': lambda t: colored(t, on_color='on_red'),
            'low': lambda t: colored(t, 'red'),
            'high': lambda t: colored(t, 'cyan'),
            'match': lambda t: colored(t, attrs=['dark']),
        }
        if check == "sacrifice":
            return colored(f"{holding}/{tower}", 'green')
        else:
            check_holding, check_tower = check
            return f"{colors[check_holding](holding)}/{colors[check_tower](tower)}"

    def load_from_rhs(self, rhs):
        holding, tower = [h.strip() for h in rhs.split("/", 1)]

        def mots(rr, my_min, my_max):
            if "-" in rr:
                sr_min, sr_max = rr.split("-")
                my_min = saturation(int(sr_min) if sr_min else None, my_min, None)
                my_max = saturation(None, my_max, int(sr_max) if sr_max else None)
            elif rr.startswith("="):
                sr = rr[1:]
                my_min = saturation(int(sr) if sr else None, my_min, None)
                my_max = saturation(None, my_max, int(sr) if sr else None)
            else:
                sr = int(rr)
                my_min = saturation(int(sr) if sr else None, my_min, None)
            return my_min, my_max

        self.holding_min, self.holding_max = mots(holding, self.holding_min, self.holding_max)
        self.tower_min, self.tower_max = mots(tower, self.tower_min, self.tower_max)


class Targets(dict):
    _class_resolver = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolver = ChainMap({}, self._class_resolver)

    def __missing__(self, key):
        self[key] = Target()
        return self[key]

    def load_line(self, line):
        if not line or line.startswith("--"):
            return
        elif ":=" in line:
            lhs, rhs = [span.strip() for span in line.split(":=", 1)]
            syntax = 'force'
        elif "<-" in line:
            lhs, rhs = [span.strip() for span in line.split("<-", 1)]
            syntax = 'macro'
        elif "=" in line:
            lhs, rhs = [span for span in line.split("=", 1)]
            syntax = 'intersect'
        else:
            raise ValueError

        # process lhs
        characters = []
        for span in lhs.split(","):
            if "/" in span:
                resolver, param = span.rsplit("/", 1)
                characters.extend(self.resolver[resolver](param))
            else:
                characters.append(int(span))

        for cid in characters:
            if syntax == 'macro':
                self[cid] = Target.clone(self[rhs])
                continue
            if syntax == 'force':
                del self[cid]
            self[cid].load_from_rhs(rhs)

    def load_lines(self, lines):
        for line in lines:
            self.load_line(line)

    def init_macros(self):
        self["Never"] = Target(0, 0, 0, 0)
        self["Love1"] = Target(520, 520, 500, 500)
        self["Love2"] = Target(520, 520, 2500, 2500)
        self["Love3"] = Target(520, 520, 12500, 12500)
        self["T1"] = Target(0, 0, 500, 500)
        self["T2"] = Target(0, 0, 2500, 2500)
        self["T3"] = Target(0, 0, 12500, 12500)
        self["CP"] = Target(0, 0, 2501, 2501)
        self["GoodTrap"] = Target(0, 0, 2502, 2502)

    def cleanup_macros(self):
        strip_keys = [key for key in self.keys() if not isinstance(key, int)]
        for key in strip_keys:
            del self[key]

    @classmethod
    def add_class_resolver(cls, *prefixes):
        def decorator(func):
            for prefix in prefixes:
                cls._class_resolver[prefix] = func
            return func

        return decorator

    def add_resolver(self, *prefixes):
        def decorator(func):
            for prefix in prefixes:
                self.resolver[prefix] = func
            return func

        return decorator


@Targets.add_class_resolver("sub", "subject")
def _target_subject_resolver(sub_id):
    from ..bgmd.api import subject_character
    for cid in subject_character(int(sub_id)):
        yield cid


@Targets.add_class_resolver("cv")
def _cv_resolver(cv_id):
    from ..bgmd import person_work_voice_character, Person
    for character in person_work_voice_character(Person(id=int(cv_id))):
        yield character.id


def level_colors(level):
    if level == 0:
        return colored(f"{level:^5}", 'grey', 'on_white', ['reverse', 'bold'])
    elif level == 1:
        return colored(f"{level:^5}", 'white', 'on_green')
    elif level == 2:
        return colored(f"{level:^5}", 'white', 'on_cyan')
    elif level == 3:
        return colored(f"{level:^5}", 'yellow', 'on_white', ['reverse', 'bold'])
    elif level == 4:
        return colored(f"{level:^5}", 'white', 'on_yellow')
    elif level == 5:
        return colored(f"{level:^5}", 'white', 'on_magenta')
    elif level == 6:
        return colored(f"{level:^5}", 'red', 'on_white', ['reverse', 'bold'])
    else:
        return colored(f"{level:^5}", 'black', 'on_white')
