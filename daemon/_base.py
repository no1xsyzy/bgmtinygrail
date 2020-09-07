import json.decoder
import logging
import os
import sys
import traceback
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from typing import *

from requests.exceptions import ReadTimeout, ConnectionError

from bgmd.model import Login
from requests_as_model import APIResponseSchemeNotMatch
from tinygrail.model import Player

logger = logging.getLogger('daemon')

try:
    from systemd.daemon import notify, Notification
except ImportError:
    class Notification(Enum):
        WATCHDOG = "WATCHDOG"
        READY = "READY"


    def notify(notification: Notification):
        logger.debug(f"no systemd support but notified: {notification}")

_TV = TypeVar('_TV')


class TooMuchExceptionsError(Exception):
    pass


class Daemon(ABC):
    player: Player
    login: Login
    error_time: List[datetime]
    error_tolerance_period: int
    error_tolerance_count: int
    as_systemd_unit: bool
    last_daily: Optional[date]
    last_hourly: Optional[datetime]

    def __init__(self, player, login, *args, **kwargs):
        self.player = player
        self.login = login
        self.error_time = []
        self.error_tolerance_period = 5
        self.error_tolerance_count = 5
        self.as_systemd_unit = ('INVOCATION_ID' in os.environ  # systemd >= v252
                                or 'BT_AS_SYSTEMD_UNIT' in os.environ)  # < v252 or for testing
        self.last_daily = None
        self.last_hourly = None

    def notify_ready(self):
        if self.as_systemd_unit:
            notify(Notification.READY)

    def notify_watchdog(self):
        if self.as_systemd_unit:
            notify(Notification.WATCHDOG)

    def safe_run(self, tick_function: Callable[..., _TV], *args, **kwargs) -> _TV:
        # we want exception not breaking
        # noinspection PyBroadException
        try:
            return tick_function(*args, **kwargs)
        except TooMuchExceptionsError:
            raise
        except Exception as e:
            now = datetime.now()
            self.error_time.append(now)
            while self.error_time and now - self.error_time[0] < timedelta(minutes=self.error_tolerance_period):
                self.error_time.pop(0)
            if isinstance(e, ReadTimeout):
                logger.warning("Read Timeout")
            elif isinstance(e, ConnectionError):
                logger.warning("Connection Error")
            else:
                with open(f"exception@{now.isoformat().replace(':', '.')}.log", mode='w', encoding='utf-8') as fp:
                    traceback.print_exc(file=fp)
                    if isinstance(e, json.decoder.JSONDecodeError):
                        print('JSONDecodeError, original doc:', file=fp)
                        print(e.doc, file=fp)
                    elif isinstance(e, APIResponseSchemeNotMatch):
                        print('Validation Error, original doc:', file=fp)
                        print(e.data, file=fp)
                    traceback.print_exc(file=fp)
                logger.warning(f"Ticking not successful, "
                               f"traceback is at: `exception@{now.isoformat().replace(':', '.')}.log`.")
            if len(self.error_time) > self.error_tolerance_count:
                logger.error(f"There has been too much (>{self.error_tolerance_count}) errors "
                             f"in past {self.error_tolerance_period} minutes, stopping.")
                raise TooMuchExceptionsError from None

    def run_forever(self, wait_seconds, *,
                    start_function=None,
                    tick_function=None,
                    finalize_function=None,
                    daily_function=None,
                    hourly_function=None,
                    ):
        from time import sleep
        try:
            self.safe_run(start_function or self.start)
            while True:
                logger.info("start tick")
                # daily
                today = date.today()
                if self.last_daily is None or self.last_daily < today:
                    update = self.safe_run(daily_function or self.daily)
                    if update:
                        self.last_daily = today
                # hourly
                hour = datetime.now().replace(minute=0, second=0, microsecond=0)
                if self.last_hourly is None or self.last_hourly < hour:
                    update = self.safe_run(hourly_function or self.hourly)
                    if update:
                        self.last_hourly = hour
                # tick
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
            self.safe_run(finalize_function or self.finalize)

    def daemon(self):
        self.run_forever(20)

    @abstractmethod
    def tick(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        self.notify_ready()

    def finalize(self, *args, **kwargs):
        pass

    def daily(self, *args, **kwargs):
        return True

    def hourly(self, *args, **kwargs):
        return True
