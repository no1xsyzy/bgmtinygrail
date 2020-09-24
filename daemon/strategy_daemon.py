#!/usr/bin/env python3
import json
import logging.config
from datetime import datetime
from typing import *

# noinspection PyUnresolvedReferences
# there is no systemd in windows
from systemd.daemon import notify, Notification

from model_link.sync_asks_collect import sync_asks_collect
from strategy import *
from tinygrail.api import all_holding, all_bids
from ._base import Daemon

logger = logging.getLogger('daemon')


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def all_bidding_ids(player):
    return [h.character_id for h in all_bids(player)]


class StrategyMap(dict, Dict[int, ABCCharaStrategy]):
    def __init__(self, player, *args, **kwargs):
        self.player = player
        super().__init__(*args, **kwargs)

    def __missing__(self, cid):
        self[cid] = BalanceStrategy(self.player, cid)
        self[cid].output()
        return self[cid]


class StrategyDaemon(Daemon):
    strategy_map: Dict[int, ABCCharaStrategy]
    error_time: List[datetime]

    def __init__(self, player, login, /, *args, **kwargs):
        super().__init__(player, login, *args, **kwargs)
        self.strategy_map = StrategyMap(player)

    def _tick_chara(self, cid):
        logger.info(f"on {cid}")
        now_state = self.strategy_map[cid]
        next_state = now_state.transition()
        if next_state.strategy != now_state.strategy:
            self.strategy_map[cid] = next_state
            logger.warning(f"transaction {cid}! "
                           f"from `{now_state.strategy.name}' "
                           f"to `{next_state.strategy.name}'")
        elif next_state.strategy == now_state.strategy == Strategy.IGNORE:
            del self.strategy_map[cid]
        else:
            self.strategy_map[cid] = next_state
        next_state.output()

    def _loads(self, fn):
        try:
            with open(fn, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    str_cid, str_strategy, str_player, json_kwargs = line.split(",", 3)
                    cid = int(str_cid)
                    int_strategy = int(str_strategy)
                    type_strategy: Type[ABCCharaStrategy] = all_strategies[Strategy(int_strategy)]
                    player = self.player
                    kwargs = json.loads(json_kwargs)
                    self.strategy_map[cid] = type_strategy(player, cid, **kwargs)
        except FileNotFoundError:
            pass

    def _dumps(self, fn):
        with open(fn, 'w', encoding="utf-8") as f:
            for strategy in self.strategy_map.values():
                print(f"{strategy.cid},{strategy.strategy.value},xsb_player,{json.dumps(strategy.kwargs)}", file=f)

    def tick(self):
        # we want exception not breaking
        # noinspection PyBroadException
        for cid in sorted({*all_bidding_ids(self.player),
                           *all_holding_ids(self.player),
                           *self.strategy_map.keys()}):
            self._tick_chara(cid)
            if self.as_systemd_unit:
                notify(Notification.WATCHDOG)
        sync_asks_collect(self.player, self.login, True)
        self._dumps("now_strategy.txt")

    def start(self):
        self._loads("now_strategy.txt")
