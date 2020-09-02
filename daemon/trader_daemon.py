#!/usr/bin/env python3
import logging.config

# noinspection PyUnresolvedReferences
# there is no systemd in windows
from systemd.daemon import notify, Notification

from model_link.sync_asks_collect import sync_asks_collect
from tinygrail.api import all_holding, all_bids
from tinygrail.api import scratch_bonus2, scratch_gensokyo, scratch_gensokyo_price
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
        super().__init__(player, login, *args, **kwargs)
        self.trader = trader_cls(player)

    def tick(self):
        for cid in sorted({*all_bidding_ids(self.player),
                           *all_holding_ids(self.player)}):
            logger.info(f"on {cid}")
            self.safe_run(self.trader.tick, cid)
            if self.as_systemd_unit:
                notify(Notification.WATCHDOG)
        sync_asks_collect(self.player, self.login, True)

    def daily(self):
        logger.info(f"daily")
        if isinstance(self.trader, GracefulTrader):
            ticker = self.trader.graceful_tick
        else:
            ticker = self.trader.tick

        while True:
            scratch_result = self.safe_run(scratch_bonus2, self.player)
            if scratch_result is None:
                logger.debug(f"scratch_bonus2   | either error or over")
                break
            for sb in scratch_result:
                logger.debug(f"scratch_bonus2   | got #{sb.id:<5} | {sb.amount=}, {sb.sell_price=}")
                self.safe_run(ticker, sb.id, sb.sell_price)
        got_value = 4000
        s_price = scratch_gensokyo_price(self.player)
        while got_value >= s_price:
            scratch_result = self.safe_run(scratch_gensokyo, self.player)
            if scratch_result is None:
                logger.debug(f"scratch_gensokyo | error")
                break
            for sb in scratch_result:
                logger.debug(f"scratch_gensokyo | got #{sb.id:<5} | {sb.amount=}, {sb.sell_price=}")
                actual_value = self.safe_run(ticker, sb.id, sb.sell_price)
                got_value += actual_value * sb.amount
            got_value = 0
            s_price = scratch_gensokyo_price(self.player)
        else:
            logger.debug(f"scratch_gensokyo | over")


if __name__ == '__main__':
    from accounts import *

    daemon = TraderDaemon(tg_xsb_player, bgm_xsb_player)
    if daemon.as_systemd_unit:
        logging.config.fileConfig('logging-journald.conf')
    else:
        logging.config.fileConfig('logging.conf')
    daemon.daemon()
