from ._base import *


class CloseOutStrategy(ABCCharaStrategy):
    strategy = Strategy.CLOSE_OUT

    def transition(self):
        self.big_c.update_user_character()
        from .ignore import IgnoreStrategy
        from .balance import BalanceStrategy
        if self.big_c.total_holding == 0:
            return self._transact(IgnoreStrategy)
        else:
            return self._transact(BalanceStrategy)

    def output(self):
        self.big_c.ensure_asks([TAsk(Price=self._exchange_price, Amount=self.big_c.total_holding)])
        self.big_c.ensure_bids([])
