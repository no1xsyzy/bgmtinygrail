import logging

import click

from db import accounts
from model_link.accounts import translate
from model_link.sync_asks_collect import sync_asks_collect as api_sync_asks_collect

logger = logging.getLogger('check_all_selling')


@click.command()
@click.argument('account')
@click.option('--override-bangumi', default=None)
@click.option('--sets/--no-sets', default=True)
def sync_asks_collect(account, override_bangumi, sets):
    _, login, player = translate(accounts.retrieve(account))
    if override_bangumi is not None:
        _, login, _ = translate(accounts.retrieve(override_bangumi))

    api_sync_asks_collect(player, login, logs=logger.info, sets=sets)
