from ._base import *


class CloseOutStrategy(ABCCharaStrategy):
    strategy = Strategy.CLOSE_OUT

    def transition(self):
        self.big_c.update_user_character()
        from strategy import IgnoreStrategy, BalanceStrategy
        if self.big_c.total_holding == 0:
            return IgnoreStrategy(self.player, self.cid)
        else:
            return BalanceStrategy(self.player, self.cid)

    def output(self):
        self.big_c.ensure_asks([TAsk(Price=self._exchange_price, Amount=self.big_c.total_holding)])
        self.big_c.ensure_bids([])
