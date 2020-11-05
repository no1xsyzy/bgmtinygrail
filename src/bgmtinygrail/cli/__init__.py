import logging.config

import click

from .accounts import accounts
from .check_auction_price_value import check_auction_price_value
from .check_cv import check_cv
from .check_targets import check_targets
from .daemon import daemon
from .dump import dump
from .force_view import force_view
from .list_top_week import list_top_week
from .magic import magic
from .rr_top import rr_top
from .spoil_highest_bid import spoil_highest_bid
from .spoil_holders import spoil_holders
from .sync_asks_collect import sync_asks_collect


@click.group()
@click.option('-L', '--log-conf', default='logging.conf')
def entry_point(log_conf):
    logging.config.fileConfig(log_conf)


assert isinstance(entry_point, click.Group)

entry_point.add_command(accounts)
entry_point.add_command(check_auction_price_value)
entry_point.add_command(check_cv)
entry_point.add_command(check_targets)
entry_point.add_command(daemon)
entry_point.add_command(dump)
entry_point.add_command(force_view)
entry_point.add_command(list_top_week)
entry_point.add_command(magic)
entry_point.add_command(spoil_highest_bid)
entry_point.add_command(spoil_holders)
entry_point.add_command(sync_asks_collect)
