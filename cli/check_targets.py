from itertools import chain
from typing import List

import click
from click.utils import LazyFile

from tinygrail.api import batch_character_info, get_full_holding
from tinygrail.model import TICO
from ._base import TG_PLAYER
from ._helpers import parse_target


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('targets', type=str, nargs=-1)
@click.option('-f', '--from-file', type=click.File('r', encoding='utf-8'), multiple=True, default=[])
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, targets: List[str], from_file: List[LazyFile], show_exceeds):
    def iterates():
        for file in from_file:
            for line in file:
                line = line.rstrip()
                if line and not line.startswith("--"):
                    yield line
        for target in targets:
            for t in target.split(","):
                yield t

    parsed_targets = parse_target(chain(iterates()))
    if any(i != (0, 0) for i in parsed_targets.items()):
        print("no target specified at all")
        raise click.exceptions.Exit(11)
    characters = get_full_holding(player)

    checks = []
    for cid, (th, tt) in parsed_targets.items():
        if cid in characters:
            ch, ct = characters[cid]
            if (not (ch >= th and ct >= tt)) or (show_exceeds and not (ch == th and ct == tt)):
                click.echo(f"#{cid:<5} | target: {th}/{tt}, actual: {ch}/{ct}")
        else:
            if (th, tt) != (0, 0):
                checks.append(cid)

    if checks:
        for c in batch_character_info(player, checks):
            if isinstance(c, TICO):
                click.echo(f"#{c.character_id:<5} | ICO")
            else:
                click.echo(f"#{c.character_id:<5} | Available")
