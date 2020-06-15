#!/usr/bin/env python3
import json
import logging.config
import traceback
from datetime import datetime, timedelta
from typing import *

import dacite.exceptions

from accounts import *
from checkallselling import check_all_selling
from strategy import *
from tinygrail.api import all_holding

logger = logging.getLogger('daemon')


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


class StrategyMap(dict):
    def __init__(self, player, *args, **kwargs):
        self.player = player
        super().__init__(*args, **kwargs)

    def __missing__(self, cid):
        self[cid] = IgnoreStrategy(self.player, cid)
        return self[cid]


class Daemon:
    strategy_map: Dict[int, ABCCharaStrategy]
    error_time: List[datetime]

    def __init__(self, player):
        self.player = player
        self.strategy_map = StrategyMap(player)
        self.error_time = []
        self.error_tolerance = 1

    def tick(self):
        # noinspection PyBroadException
        try:
            for cid in {*all_holding_ids(self.player), *self.strategy_map.keys()}:
                self.tick_chara(cid)
            check_all_selling(tg_xsb_player, bgm_xsb_player, True)
        except Exception as e:
            now = datetime.now()
            self.error_time.append(now)
            while self.error_time and now - self.error_time[0] < timedelta(minutes=1):
                self.error_time.pop(0)
            with open(f"exception@{now.isoformat().replace(':', '.')}.log", mode='w') as fp:
                import sys
                traceback.print_exc(file=fp)
                if isinstance(e, json.decoder.JSONDecodeError):
                    print('JSONDecodeError, original doc:', file=fp)
                    print(e.doc, file=fp)
                if isinstance(e, dacite.exceptions.MissingValueError):
                    print('MissingValueError, original dict:', file=fp)
                    import inspect
                    from pprint import pprint
                    original_data = inspect.trace()[-1][0].f_locals['data']
                    pprint(original_data, stream=fp)
            logger.warning(f"Ticking not successful, "
                           f"traceback is at: `exception@{now.isoformat().replace(':', '.')}.log`.")
            if len(self.error_time) > 5:
                logger.error("There has been too much (>5) errors in past 1 minutes, stopping.")
                raise

    def tick_chara(self, cid):
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

    def run_forever(self, wait_seconds, *, hook_after_tick=None):
        from time import sleep
        try:
            while True:
                logger.info("start tick")
                self.tick()
                logger.info("finish run, sleeping")
                if callable(hook_after_tick):
                    hook_after_tick()
                for waited in range(wait_seconds):
                    sleep(1)
                    print(f"{waited + 1}/{wait_seconds} seconds passed", end="\r")
        except KeyboardInterrupt:
            print("\rbreak")

    def loads(self, fn):
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

    def dumps(self, fn):
        with open(fn, 'w', encoding="utf-8") as f:
            for strategy in self.strategy_map.values():
                print(f"{strategy.cid},{strategy.strategy.value},xsb_player,{json.dumps(strategy.kwargs)}", file=f)

    def daemon(self):
        self.loads("now_strategy.txt")
        self.run_forever(20, hook_after_tick=lambda: self.dumps("now_strategy.txt"))


if __name__ == '__main__':
    daemon = Daemon(tg_xsb_player)
    logging.config.fileConfig('logging.conf')
    daemon.daemon()
