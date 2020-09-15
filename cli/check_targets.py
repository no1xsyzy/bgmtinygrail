import click

from tinygrail.api import batch_character_info, get_full_holding
from tinygrail.model import TICO
from ._base import TG_PLAYER
from ._helpers import parse_target


@click.command()
@click.option('--player', type=TG_PLAYER)
@click.option('--target', type=str)
@click.option('--show-exceeds/--hide-exceeds')
def check_targets(player, target, show_exceeds):
    targets = parse_target(target.split(","))
    characters = get_full_holding(player)

    checks = []
    for cid, (th, tt) in targets.items():
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
