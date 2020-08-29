import json.decoder
import logging
import os
import sys
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import *

from requests.exceptions import ReadTimeout

from bgmd.model import Login
from requests_as_model import APIResponseSchemeNotMatch
from tinygrail.model import Player

logger = logging.getLogger('daemon')


class TooMuchExceptionsError(Exception):
    pass


class Daemon(ABC):
    player: Player
    login: Login
    error_time: List[datetime]
    error_tolerance_period: int
    error_tolerance_count: int
    as_systemd_unit: bool

    def __init__(self, player, login, *args, **kwargs):
        self.player = player
        self.login = login
        self.error_time = []
        self.error_tolerance_period = 5
        self.error_tolerance_count = 5
        self.as_systemd_unit = ('INVOCATION_ID' in os.environ  # systemd >= v252
                                or 'BT_AS_SYSTEMD_UNIT' in os.environ)  # < v252 or for testing

    def safe_run(self, tick_function):
        # we want exception not breaking
        # noinspection PyBroadException
        try:
            tick_function()
        except Exception as e:
            now = datetime.now()
            self.error_time.append(now)
            while self.error_time and now - self.error_time[0] < timedelta(minutes=self.error_tolerance_period):
                self.error_time.pop(0)
            if isinstance(e, ReadTimeout):
                logger.warning("Read Timeout")
            else:
                with open(f"exception@{now.isoformat().replace(':', '.')}.log", mode='w', encoding='utf-8') as fp:
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

    def run_forever(self, wait_seconds, *, start_function=None, tick_function=None, finalize_function=None):
        from time import sleep
        try:
            self.safe_run(start_function or self.start)
            while True:
                logger.info("start tick")
                self.safe_run(tick_function or self.tick)
                logger.info("finish run, sleeping")
                if sys.stdout.isatty():
                    for waited in range(wait_seconds):
                        sleep(1)
                        print(f"{waited + 1}/{wait_seconds} seconds passed", end="\r")
                else:
                    sleep(wait_seconds)
        except KeyboardInterrupt:
            if sys.stdout.isatty():
                print("\rbreak")
        finally:
            self.safe_run(finalize_function or self.finalize())

    def daemon(self):
        self.run_forever(20)

    @abstractmethod
    def tick(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        pass

    def finalize(self, *args, **kwargs):
        pass
