#!/usr/bin/env python3
import logging.config

# noinspection PyUnresolvedReferences
# there is no systemd in windows
from systemd.daemon import notify, Notification

from model_link.sync_asks_collect import sync_asks_collect
from tinygrail.api import all_holding, all_bids
from trader import *
from ._base import Daemon

logger = logging.getLogger('daemon')


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def all_bidding_ids(player):
    return [h.character_id for h in all_bids(player)]


class TraderDaemon(Daemon):
    trader: ABCTrader

    def __init__(self, player, login, /, *args, trader_cls=GracefulTrader, **kwargs):
        super().__init__(self, player, login, *args, **kwargs)
        self.trader = trader_cls(player)

    def tick(self):
        for cid in sorted({*all_bidding_ids(self.player),
                           *all_holding_ids(self.player)}):
            logger.info(f"on {cid}")
            self.trader.tick(cid)
            if self.as_systemd_unit:
                notify(Notification.WATCHDOG)
        sync_asks_collect(self.player, self.login, True)


if __name__ == '__main__':
    from accounts import *

    daemon = TraderDaemon(tg_xsb_player, bgm_xsb_player)
    if daemon.as_systemd_unit:
        logging.config.fileConfig('logging-journald.conf')
    else:
        logging.config.fileConfig('logging.conf')
    daemon.daemon()
