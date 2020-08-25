import click

from .accounts import accounts
from .check_auction_price_value import check_auction_price_value
from .check_cv import check_cv
from .magic import magic


@click.group()
def entry_point():
    pass


assert isinstance(entry_point, click.Group)

entry_point.add_command(accounts)
entry_point.add_command(check_auction_price_value)
entry_point.add_command(check_cv)
entry_point.add_command(magic)
