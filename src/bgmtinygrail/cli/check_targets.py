from itertools import chain
from typing import List

import click
from click.utils import LazyFile

from ._base import TG_PLAYER
from ._helpers import parse_target
from ..tinygrail.api import batch_character_info, get_full_holding_2
from ..tinygrail.model import TICO, TTemple


@click.command()
@click.argument('player', type=TG_PLAYER)
@click.argument('targets', type=str, nargs=-1)
@click.option('-f', '--from-file', type=click.File('r', encoding='utf-8'), multiple=True, default=[])
@click.option('-o', '--output-format', default='simple')
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, targets: List[str], from_file: List[LazyFile], show_exceeds, output_format):
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
    if not any(i != (0, 0) for i in parsed_targets.items()):
        print("no target specified at all")
        raise click.exceptions.Exit(11)
    characters = get_full_holding_2(player)

    table = {}
    checks = []
    for cid, (th, tt) in parsed_targets.items():
        if character := characters.get(cid):
            if isinstance(character, TTemple):
                ch = 0
                ct = character.sacrifices
            else:
                ch, ct = character.state, character.sacrifices
            if (not (ch >= th and ct >= tt)) or (show_exceeds and not (ch == th and ct == tt)):
                table[cid] = [f"#{cid}", character.name, f"target: {th}/{tt}, actual: {ch}/{ct}"]
        else:
            if (th, tt) != (0, 0):
                checks.append(cid)

    if checks:
        for c in batch_character_info(player, checks):
            if isinstance(c, TICO):
                table[c.character_id] = [f"#{c.character_id}", c.name, "ICO"]
            else:
                table[c.character_id] = [f"#{c.character_id}", c.name, "Available"]

    from tabulate import tabulate
    click.echo(tabulate([table[key] for key in table.keys()], ('CID', 'name', 'Detail'), output_format))
