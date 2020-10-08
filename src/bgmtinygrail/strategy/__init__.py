from typing import *

from ._base import Strategy, ABCCharaStrategy
from .balance import BalanceStrategy
from .buy_in import BuyInStrategy
from .close_out import CloseOutStrategy
from .ignore import IgnoreStrategy
from .manual_control import ManualControlStrategy
from .self_service import SelfServiceStrategy
from .show_grace import ShowGraceStrategy

all_strategies: Dict[Strategy, Type[ABCCharaStrategy]] = {}

for _strategy in ABCCharaStrategy.__subclasses__():
    all_strategies[_strategy.strategy] = _strategy

del _strategy

__all__ = ['Strategy', 'ABCCharaStrategy',
           'BalanceStrategy', 'BuyInStrategy', 'CloseOutStrategy', 'IgnoreStrategy', 'SelfServiceStrategy',
           'ShowGraceStrategy',
           'all_strategies']
