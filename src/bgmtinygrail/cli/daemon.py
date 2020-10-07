import logging.config

import click

from ..db import accounts as db_accounts
from ..model_link.accounts import translate


@click.group()
def daemon():
    pass


@daemon.command()
@click.option("--daemon-type", type=click.Choice(['trader', 'strategy']), default='trader')
@click.option("--trader-type", type=click.Choice(['fundamental', 'graceful', 'strategical']), default='strategical')
@click.option("--account")
def start(daemon_type, trader_type, account):
    if daemon_type == 'trader':
        from ..daemon.trader_daemon import TraderDaemon
        daemon_cls = TraderDaemon
    elif daemon_type == 'strategy':
        from ..daemon.strategy_daemon import StrategyDaemon
        daemon_cls = StrategyDaemon
    else:
        print("no such daemon")
        raise click.exceptions.Exit(13)

    _, login, player = translate(db_accounts.retrieve(account))

    if trader_type == 'fundamental':
        from ..trader import FundamentalTrader
        trader_cls = FundamentalTrader
    elif trader_type == 'graceful':
        from ..trader import GracefulTrader
        trader_cls = GracefulTrader
    elif trader_type == 'strategical':
        from ..trader import StrategicalTrader
        trader_cls = StrategicalTrader
    else:
        print("no such trader")
        raise click.exceptions.Exit(14)

    d = daemon_cls(player, login, trader_cls=trader_cls)

    if d.as_systemd_unit:
        logging.config.fileConfig('logging-journald.conf')
    else:
        logging.config.fileConfig('logging.conf')

    d.run_forever(20)
