from typing import *

from ._base import Strategy, ABCCharaStrategy
from .balance import BalanceStrategy
from .buy_in import BuyInStrategy
from .close_out import CloseOutStrategy
from .ignore import IgnoreStrategy
from .self_service import SelfServiceStrategy

all_strategies: Dict[Strategy, Type[ABCCharaStrategy]] = {
    Strategy.IGNORE: IgnoreStrategy,
    Strategy.CLOSE_OUT: CloseOutStrategy,
    Strategy.BALANCE: BalanceStrategy,
    Strategy.SELF_SERVICE: SelfServiceStrategy,
    Strategy.BUY_IN: BuyInStrategy,
}

__all__ = ['Strategy', 'ABCCharaStrategy',
           'BalanceStrategy', 'BuyInStrategy', 'CloseOutStrategy', 'IgnoreStrategy', 'SelfServiceStrategy',
           'all_strategies']
