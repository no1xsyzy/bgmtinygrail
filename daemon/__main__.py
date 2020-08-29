import os

import click

from db import accounts as db_accounts
from model_link.accounts import translate


@click.group()
def daemon():
    pass


@daemon.command()
@click.option("--fork/--no-fork", default=True)
@click.option("--pid-file", default=None)
@click.option("--daemon-type", type=click.Choice(['trader', 'strategy']), default='trader')
@click.option("--account")
def start(fork, pid_file, daemon_type, account):
    if daemon_type == 'trader':
        from .trader_daemon import TraderDaemon
        daemon_cls = TraderDaemon
    elif daemon_type == 'strategy':
        from .strategy_daemon import StrategyDaemon
        daemon_cls = StrategyDaemon
    else:
        print("no such trader")
        raise click.exceptions.Exit(13)

    players_dicts = db_accounts.retrieve(account)
    if len(players_dicts) == 0:
        print("No such account!")
        raise click.exceptions.Exit(1)
    _, login, player = translate(db_accounts.retrieve(account)[0])

    d = daemon_cls(player, login)

    if fork:
        child_pid = os.fork()
        if pid_file is not None:
            with open(pid_file, mode='w', encoding='ascii') as fp:
                print(child_pid, file=fp)
        return

    try:
        d.run_forever(20)
    finally:
        if fork:
            os.remove(pid_file)


daemon()
