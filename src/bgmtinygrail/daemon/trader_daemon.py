#!/usr/bin/env python3
import logging.config
import re
from random import sample
from typing import *

from ._base import Daemon
from ..model_link.sync_asks_collect import sync_asks_collect
from ..tinygrail import ServerSentError
from ..tinygrail.api import all_holding, all_bids
from ..tinygrail.api import get_daily_bonus, get_weekly_share, scratch_bonus2, scratch_gensokyo, scratch_gensokyo_price
from ..tinygrail.api import get_history
from ..trader import *

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
        to_update = sorted(self.urgent_chars.union(sample(self.slow_chars, k=3) if len(self.slow_chars) > 3
                                                   else self.slow_chars))
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
        self.notify_watchdog()
        if hasattr(self.trader, 'graceful_tick'):
            ticker = self.trader.graceful_tick
        else:
            ticker = self.trader.tick

        # daily bonus (cc)
        try:
            s = get_daily_bonus(self.player)
            q = re.findall(r"[\d.]+(?=cc)", s)
            logger.info(f"get_daily_bonus  | got {float(q[0])} cc")
        except ServerSentError as e:
            if e.state == 1 and e.message == '今日已经领取过登录奖励。':
                logger.debug(f"get_daily_bonus  | already got")
            else:
                raise

        # weekly share
        from datetime import date
        if date.today().isoweekday() == 6:
            try:
                s = get_weekly_share(self.player)
                q = re.findall(r"[\d.]+(?=cc)", s)
                q0 = float(q[0])
                q1 = float(q[1])
                logger.info(f"get_weekly_share | got {q0}-{q1}={q0 - q1} cc")
            except ServerSentError as e:
                if e.state == 1 and e.message == '您已经领取过本周奖励。':
                    logger.debug(f"get_weekly_share | already got")
                else:
                    raise

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
                self.safe_run(ticker, sb.id, sb.sell_price)
            s_price = scratch_gensokyo_price(self.player)
        else:
            logger.debug("scratch_gensokyo | over")
        return True

    def hourly(self):
        abi = set(all_bidding_ids(self.player))
        ahi = set(all_holding_ids(self.player))

        self.slow_chars.update(abi)
        logger.debug(f"{sorted(self.slow_chars)=}")

        # holding but not bidding, indicating worn out bidding
        self.urgent_chars.update(ahi - abi)
        # bidding but not holding, includes force-view
        self.urgent_chars.update(abi - ahi)
        logger.debug(f"{sorted(self.urgent_chars)=}")
        return True

    def start(self):
        super().start()
        self._update_character_due_to_history(full_update=True)
