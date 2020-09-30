from ._base import *


class IgnoreStrategy(ABCCharaStrategy):
    strategy = Strategy.IGNORE

    def transition(self):
        from strategy import BalanceStrategy
        if self.big_c.total_holding > 0:
            logger.info("new stock")
            self._fast_seller(low=self._exchange_price)
            if self.big_c.amount or self.big_c.asks:
                return self._transact(BalanceStrategy)
        elif self.big_c.bids[0].price == 2.0 and self.big_c.bids[0].amount == 2:
            logger.info("forced view")
            self._fast_forward(self._exchange_price)
            self._output_balanced()
        return self

    def output(self):
        self.big_c.ensure_asks([], force_updates='before')
        self.big_c.ensure_bids([], force_updates='after')
