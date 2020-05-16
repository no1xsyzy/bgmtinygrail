#!/usr/bin/env python3
from strategy import *
from accounts import *
import traceback
from datetime import datetime, timedelta
import json
import logging
import logging.config

logger = logging.getLogger('daemon')


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


class Daemon:
    strategy_map: Dict[int, ABCCharaStrategy]
    error_time: List[datetime]

    def __init__(self, player):
        self.player = player
        self.strategy_map = {}
        self.error_time = []
        self.error_tolerance = 1

    def init_strategy_cid(self, cid):
        self.strategy_map[cid] = IgnoreStrategy(self.player, cid)

    def tick(self):
        # noinspection PyBroadException
        try:
            for cid in {*all_holding_ids(self.player), *self.strategy_map.keys()}:
                self.tick_chara(cid)
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
            logger.warning(f"Ticking not successful, "
                           f"traceback is at: `exception@{now.isoformat().replace(':', '.')}.log`.")
            if len(self.error_time) > 5:
                logger.error("There has been too much (>5) errors in past 1 minutes, stopping.")
                raise

    def tick_chara(self, cid):
        logger.info(f"on {cid}")
        if cid not in self.strategy_map:
            self.init_strategy_cid(cid)
        now_state = self.strategy_map[cid]
        next_state = now_state.transition()
        if next_state.strategy != now_state.strategy:
            self.strategy_map[cid] = next_state
            logger.warning(f"transaction {cid}! "
                           f"from `{now_state.strategy.name}' "
                           f"to `{next_state.strategy.name}'")
        elif next_state.strategy == now_state.strategy == Strategy.IGNORE:
            del self.strategy_map[cid]
        next_state.output()


if __name__ == '__main__':
    daemon = Daemon(tg_xsb_player)
    logging.config.fileConfig('logging.conf')
    from time import sleep
    while True:
        logger.info("start tick")
        daemon.tick()
        logger.info("finish run, sleeping")
        SECONDS = 20
        for i in range(SECONDS):
            sleep(1)
            print(f"{i + 1}/{SECONDS} seconds passed", end="\r")
