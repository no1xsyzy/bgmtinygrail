#!/usr/bin/env python3
import logging.config
import traceback
from datetime import datetime, timedelta

from accounts import *
from checkallselling import check_all_selling
from strategy import *

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

    def run_forever(self, wait_seconds):
        from time import sleep
        try:
            while True:
                logger.info("start tick")
                self.tick()
                logger.info("finish run, sleeping")
                for waited in range(wait_seconds):
                    sleep(1)
                    print(f"{waited + 1}/{wait_seconds} seconds passed", end="\r")
        except KeyboardInterrupt:
            print("\rbreak")

    def daemon(self):
        self.run_forever(20)


if __name__ == '__main__':
    daemon = Daemon(tg_xsb_player)
    logging.config.fileConfig('logging.conf')
    daemon.daemon()
