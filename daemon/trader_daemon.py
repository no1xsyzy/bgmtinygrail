#!/usr/bin/env python3
import logging.config
import math
from typing import *

from model_link.sync_asks_collect import sync_asks_collect
from tinygrail.api import all_holding, all_bids
from tinygrail.api import get_history
from tinygrail.api import scratch_bonus2, scratch_gensokyo, scratch_gensokyo_price
from trader import *
from ._base import Daemon
from random import sample

logger = logging.getLogger('daemon')


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def all_bidding_ids(player):
    return [h.character_id for h in all_bids(player)]


class TraderDaemon(Daemon):
    trader: ABCTrader
    last_history_id: int
    urgent_chars: Set[int]
    slow_chars: Set[int]

    def __init__(self, player, login, /, *args, trader_cls=GracefulTrader, **kwargs):
        super().__init__(player, login, *args, **kwargs)
        self.trader = trader_cls(player)
        self.last_history_id = 0
        self.urgent_chars = set()
        self.slow_chars = set()

    def _update_character_due_to_history(self, full_update=False) -> List[int]:
        if full_update or self.last_history_id == 0:
            histories = get_history(self.player, page_limit=1)
            self.last_history_id = histories[0].id
            return []
        histories = get_history(self.player, since_id=self.last_history_id)
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
        self.urgent_chars.update(self._update_character_due_to_history())
        to_update = sorted({*self.urgent_chars, *sample(self.slow_chars, k=math.ceil(len(self.slow_chars) / 5))})
        logger.debug(f"{to_update=}")
        for cid in to_update:
            logger.info(f"on {cid}")
            self.safe_run(self._tick_one, cid)
            self.notify_watchdog()
        sync_asks_collect(self.player, self.login, True)

    def _tick_one(self, cid):
        self.trader.tick(cid)
        if cid in self.urgent_chars:
            self.urgent_chars.remove(cid)
        if cid in self.slow_chars:
            self.slow_chars.remove(cid)

    def daily(self):
        logger.info("daily")
        self.notify_watchdog()
        if isinstance(self.trader, GracefulTrader):
            ticker = self.trader.graceful_tick
        else:
            ticker = self.trader.tick

        # bonus2
        while True:
            scratch_result = self.safe_run(scratch_bonus2, self.player)
            self.notify_watchdog()
            if scratch_result is None:
                logger.debug("scratch_bonus2   | either error or over")
                break
            for sb in scratch_result:
                logger.debug(f"scratch_bonus2   | got #{sb.id:<5} | {sb.amount=}, {sb.sell_price=}")
                self.safe_run(ticker, sb.id, sb.sell_price)
        # gensokyo
        got_value = 4000
        s_price = scratch_gensokyo_price(self.player)
        while got_value >= s_price:
            scratch_result = self.safe_run(scratch_gensokyo, self.player)
            self.notify_watchdog()
            if scratch_result is None:
                logger.debug("scratch_gensokyo | error")
                break
            for sb in scratch_result:
                logger.debug(f"scratch_gensokyo | got #{sb.id:<5} | {sb.amount=}, {sb.sell_price=}")
                actual_value = self.safe_run(ticker, sb.id, sb.sell_price) or 0
                got_value += actual_value * sb.amount
            got_value = 0
            s_price = scratch_gensokyo_price(self.player)
        else:
            logger.debug("scratch_gensokyo | over")
        return True

    def hourly(self):
        logger.info("hourly")
        abi = set(all_bidding_ids(self.player))
        ahi = set(all_holding_ids(self.player))

        self.slow_chars.update(abi)
        logger.debug(f"{sorted(self.slow_chars)=}")

        # holding but not bidding, indicating worn out bidding
        self.urgent_chars.update(ahi-abi)
        logger.debug(f"{sorted(self.urgent_chars)=}")
        return True

    def start(self):
        super().start()
        self._update_character_due_to_history(full_update=True)
