#!/usr/bin/env python3
import json
import logging.config
import sys
import traceback
from datetime import datetime, timedelta
from typing import *

from requests.exceptions import ReadTimeout

from bgmd.model import Login
from model_link.sync_asks_collect import sync_asks_collect
from requests_as_model import APIResponseSchemeNotMatch
from tinygrail.api import all_holding, all_bids
from tinygrail.model import Player
from trader import *

logger = logging.getLogger('daemon')


class TooMuchExceptionsError(Exception):
    pass


def all_holding_ids(player):
    return [h.character_id for h in all_holding(player)]


def all_bidding_ids(player):
    return [h.character_id for h in all_bids(player)]


class Daemon:
    player: Player
    login: Login
    trader: ABCTrader
    error_time: List[datetime]

    def __init__(self, player, login, *, trader_cls=GracefulTrader):
        self.player = player
        self.login = login
        self.trader = trader_cls(player)
        self.error_time = []
        self.error_tolerance_period = 5
        self.error_tolerance_count = 5

    def tick(self):
        # we want exception not breaking
        # noinspection PyBroadException
        try:
            for cid in sorted({*all_bidding_ids(self.player),
                               *all_holding_ids(self.player)}):
                logger.info(f"on {cid}")
                self.trader.tick(cid)
            sync_asks_collect(self.player, self.login, True)
        except Exception as e:
            now = datetime.now()
            self.error_time.append(now)
            while self.error_time and now - self.error_time[0] < timedelta(minutes=self.error_tolerance_period):
                self.error_time.pop(0)
            if isinstance(e, ReadTimeout):
                logger.warning("Read Timeout")
            else:
                with open(f"exception@{now.isoformat().replace(':', '.')}.log", mode='w', encoding='utf-8') as fp:
                    import sys
                    traceback.print_exc(file=fp)
                    if isinstance(e, json.decoder.JSONDecodeError):
                        print('JSONDecodeError, original doc:', file=fp)
                        print(e.doc, file=fp)
                    elif isinstance(e, APIResponseSchemeNotMatch):
                        print('Validation Error, original doc:', file=fp)
                        print(e.data, file=fp)
                logger.warning(f"Ticking not successful, "
                               f"traceback is at: `exception@{now.isoformat().replace(':', '.')}.log`.")
            if len(self.error_time) > self.error_tolerance_count:
                logger.error(f"There has been too much (>{self.error_tolerance_count}) errors "
                             f"in past {self.error_tolerance_period} minutes, stopping.")
                raise TooMuchExceptionsError from None

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
                    if sys.stdout.isatty():
                        print(f"{waited + 1}/{wait_seconds} seconds passed", end="\r")
        except KeyboardInterrupt:
            if sys.stdout.isatty():
                print("\rbreak")

    def daemon(self):
        self.run_forever(20)


if __name__ == '__main__':
    from accounts import *

    daemon = Daemon(tg_xsb_player, bgm_xsb_player)
    logging.config.fileConfig('logging.conf')
    daemon.daemon()
