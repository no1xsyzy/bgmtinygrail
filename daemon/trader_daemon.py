#!/usr/bin/env python3
import logging.config
from enum import Enum
from typing import *

from model_link.sync_asks_collect import sync_asks_collect
from tinygrail.api import all_holding, all_bids
from tinygrail.api import get_history_since_id
from tinygrail.api import scratch_bonus2, scratch_gensokyo, scratch_gensokyo_price
from trader import *
from ._base import Daemon

logger = logging.getLogger('daemon')

try:
    from systemd.daemon import notify, Notification
except ImportError:
    class Notification(Enum):
        WATCHDOG = "WATCHDOG"


    def notify(notification: Notification):
        logger.debug(f"no systemd support but notified: {notification}")


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def all_bidding_ids(player):
    return [h.character_id for h in all_bids(player)]


class TraderDaemon(Daemon):
    trader: ABCTrader
    last_history_id: int

    def __init__(self, player, login, /, *args, trader_cls=GracefulTrader, **kwargs):
        super().__init__(player, login, *args, **kwargs)
        self.trader = trader_cls(player)
        self.last_history_id = 0

    def _update_character_due_to_history(self, full_update=False) -> List[int]:
        if full_update or self.last_history_id == 0:
            histories = get_history_since_id(self.player, page_limit=1)
            self.last_history_id = histories[0].id
            return sorted({*all_bidding_ids(self.player),
                           *all_holding_ids(self.player)})
        histories = get_history_since_id(self.player, self.last_history_id)
        update_characters = set()
        for history in histories:
            if history.id > self.last_history_id:
                if hasattr(history, 'character_id'):
                    update_characters.add(history.character_id)
            else:
                break
        if histories:
            self.last_history_id = histories[0].id
        return sorted(update_characters)

    def tick(self):
        to_update = self._update_character_due_to_history()
        for cid in to_update:
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
        return True

    def hourly(self):
        to_update = self._update_character_due_to_history(full_update=True)
        for cid in to_update:
            logger.info(f"on {cid}")
            self.safe_run(self.trader.tick, cid)
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
