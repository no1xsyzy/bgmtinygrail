import logging.config
import os

import click

from ..db import accounts as db_accounts
from ..model_link.accounts import translate


@click.group()
def daemon():
    pass


@daemon.command()
@click.option("--fork/--no-fork", default=True)
@click.option("--pid-file", default=None)
@click.option("--daemon-type", type=click.Choice(['trader', 'strategy']), default='trader')
@click.option("--trader-type", type=click.Choice(['fundamental', 'graceful', 'strategical']), default='strategical')
@click.option("--account")
def start(fork, pid_file, daemon_type, trader_type, account):
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

    if fork:
        child_pid = os.fork()
        if pid_file is not None:
            with open(pid_file, mode='w', encoding='ascii') as fp:
                print(child_pid, file=fp)
        return

    if d.as_systemd_unit:
        logging.config.fileConfig('logging-journald.conf')
    else:
        logging.config.fileConfig('logging.conf')

    try:
        d.run_forever(20)
    finally:
        if fork:
            os.remove(pid_file)
