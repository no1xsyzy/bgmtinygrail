import re
from typing import Iterable, Dict, Tuple

import click

__all__ = ['parse_target']

PARSER_RE = re.compile(r"(?:(?P<cid>\d+)|cv/(?P<cv_id>\d+)|(?:sub|subject)/(?P<sub_id>\d+))"
                       r" *= *"
                       r"(?P<hold>\d+)?(?:/(?P<tower>\d*))?")


def parse_target(targets: Iterable[str]) -> Dict[int, Tuple[int, int]]:
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
