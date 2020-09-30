from ._base import *


class BalanceStrategy(ABCCharaStrategy):
    strategy = Strategy.BALANCE

    def transition(self):
        from .ignore import IgnoreStrategy
        if self.big_c.total_holding == 0:
            return self._transact(IgnoreStrategy)
        if self.big_c.amount > 0:
            logger.info("there is some part not selling")
            if not self.big_c.bids:
                logger.info("and bids ran out")
                self._fast_forward()
            return self
        elif self.big_c.asks[0].price != self._exchange_price:
            logger.info(f"exchange price not match ({self.big_c.asks[0].price} != {self._exchange_price})")
            return self
        return self

    def output(self):
        self._output_balanced()
