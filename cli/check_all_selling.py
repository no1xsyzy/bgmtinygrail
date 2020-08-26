import logging

import click

from bgmd.api import user_mono, collect_mono, erase_collect_mono
from db import accounts
from model_link.accounts import translate
from tinygrail.api import all_asks

logger = logging.getLogger('check_all_selling')


@click.command()
@click.argument('account')
@click.option('--override-bangumi', default=None)
@click.option('--sets/--no-sets', default=True)
def cmd_check_all_selling(account, override_bangumi, sets):
    _, login, player = translate(accounts.retrieve(account)[0])
    if override_bangumi is not None:
        _, login, _ = translate(accounts.retrieve(override_bangumi)[0])

    asks = {c.character_id for c in all_asks(player)}

    favorite_characters = {c.id for c in user_mono(login.user, 'character')}

    for i in asks - favorite_characters:
        logger.info(f"+ https://bgm.tv/character/{i}")
        if sets:
            collect_mono(login, i)

    for i in favorite_characters - asks:
        logger.info(f"- https://bgm.tv/character/{i}")
        if sets:
            erase_collect_mono(login, i)
