from ._base import *


class BuyInStrategy(ABCCharaStrategy):
    strategy = Strategy.BUY_IN

    def transition(self):
        return self

    def output(self):
        self.big_c.ensure_asks([])
        self.big_c.ensure_bids([TBid(Price=self._exchange_price, Amount=100)])
