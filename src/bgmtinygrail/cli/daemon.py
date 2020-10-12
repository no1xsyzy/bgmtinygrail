import logging.config
import os

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


@daemon.group()
def generate_config():
    pass


@generate_config.command()
@click.option('-d', '--working-directory', type=click.Path(exists=True, file_okay=False), default=None)
@click.option('-e', '--virtualenv', type=click.Path(exists=True, file_okay=False), default=None)
@click.option('-s', '--watchdog-seconds', type=int, default=60)
def systemd(working_directory, virtualenv, watchdog_seconds):
    virtualenv = virtualenv or os.environ['VIRTUAL_ENV']
    if virtualenv is None:
        click.echo("Should run with virtualenv", err=True)
        raise click.exceptions.Exit(15)
    print("[Unit]")
    print("Description=Bangumi TinyGrail Daemon")
    print()
    print("[Service]")
    print(f"WorkingDirectory={working_directory or os.getcwd()}")
    print(f"ExecStart={virtualenv or os.environ['VIRTUAL_ENV']}/bin/bgmtinygrail daemon start --account %i")
    print("Restart=always")
    print(f"WatchdogSec={watchdog_seconds}")
    print("WatchdogSignal=SIGINT")
    print()
    print("[Install]")
    print("WantedBy=default.target")
