import json
from datetime import datetime
from typing import List, Dict
from weakref import proxy

from sqlalchemy.orm.exc import NoResultFound

from db.strategy import get_strategy, set_strategy, purge_strategy, loads_strategy
from strategy import IgnoreStrategy, ABCCharaStrategy, Strategy, all_strategies
from tinygrail.api import user_assets
from tinygrail.player import Player
from ._base import *


class StrategyMap(dict, Dict[int, ABCCharaStrategy]):
    player: Player
    player_id_str: str

    def __init__(self, player, trader, *args, **kwargs):
        self.player = player
        self.player_id_str = str(user_assets(player).id)
        self.trader = proxy(trader)
        for cid, (strategy_id, kw) in loads_strategy(self.player_id_str).items():
            strategy = all_strategies[Strategy(strategy_id)](self.player, cid, trader=self.trader, **json.loads(kw))
            super(StrategyMap, self).__setitem__(cid, strategy)
        super().__init__(*args, **kwargs)

    def __missing__(self, cid):
        try:
            strategy_id, kwargs = get_strategy(cid, self.player_id_str)
            strategy = all_strategies[Strategy(strategy_id)](self.player, cid, trader=self.trader, **json.loads(kwargs))
            super(StrategyMap, self).__setitem__(cid, strategy)
        except NoResultFound:
            self[cid] = IgnoreStrategy(self.player, cid, trader=self.trader)
            return self[cid]

    def __setitem__(self, cid, strategy: ABCCharaStrategy):
        super(StrategyMap, self).__setitem__(cid, strategy)
        set_strategy(cid, self.player_id_str, strategy.strategy.value, json.dumps(strategy.kwargs))

    def __delitem__(self, cid):
        super(StrategyMap, self).__delitem__(cid)
        purge_strategy(cid, self.player_id_str)


class StrategicalTrader(ABCTrader):
    strategy_map: Dict[int, ABCCharaStrategy]
    error_time: List[datetime]
    internal_rate: float

    def __init__(self, player: Player):
        super().__init__(player)
        self.strategy_map = StrategyMap(player, self)
        self.update_internal_rate()

    def update_internal_rate(self):
        self.internal_rate = 0.1

    def tick(self, cid):
        now_state = self.strategy_map[cid]
        next_state = now_state.transition()
        if next_state is now_state:
            if next_state.strategy is Strategy.IGNORE:
                del self.strategy_map[cid]
        elif next_state.strategy != now_state.strategy:
            self.strategy_map[cid] = next_state
            logger.warning(f"transaction #{cid}! "
                           f"from `{now_state.strategy.name}' "
                           f"to `{next_state.strategy.name}'")
        else:
            self.strategy_map[cid] = next_state
        next_state.output()
