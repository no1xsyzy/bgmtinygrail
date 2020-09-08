import logging
from abc import ABCMeta, abstractmethod
from functools import lru_cache

from tinygrail.bigc import BigC
from tinygrail.model import TAsk, TBid
from tinygrail.player import Player

logger = logging.getLogger('strategy')

__all__ = ['ABCTrader', 'TAsk', 'TBid', 'logger']


@lru_cache()
def big_c(player, cid):
    return BigC(player, cid)


all_traders = {}


class TraderMeta(ABCMeta):
    def __new__(mcs, name, bases, dct):
        x = super().__new__(mcs, name, bases, dct)
        if name == 'ABCTrader':
            x.all_traders = all_traders
        else:
            all_traders[name] = x
        return x


class ABCTrader(metaclass=TraderMeta):
    player: Player

    def __init__(self, player):
        self.player = player

    def big_c(self, cid):
        res = big_c(self.player, cid)
        res.update()
        return res

    @abstractmethod
    def tick(self, cid):
        pass
