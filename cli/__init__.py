import logging.config

import click

from .accounts import accounts
from .check_all_selling import cmd_check_all_selling
from .check_auction_price_value import check_auction_price_value
from .check_cv import check_cv
from .magic import magic


@click.group()
@click.option('-L', '--log-conf', default='logging.conf')
def entry_point(log_conf):
    logging.config.fileConfig(log_conf)


assert isinstance(entry_point, click.Group)

entry_point.add_command(accounts)
entry_point.add_command(cmd_check_all_selling)
entry_point.add_command(check_auction_price_value)
entry_point.add_command(check_cv)
entry_point.add_command(magic)
