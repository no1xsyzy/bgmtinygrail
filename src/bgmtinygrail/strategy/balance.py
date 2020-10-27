from ._base import *


class BalanceStrategy(ABCCharaStrategy):
    strategy = Strategy.BALANCE

    def transition(self):
        from .ignore import IgnoreStrategy
        # if (not self.big_c.bids_all or
        #         max(self.big_c.bids_all).price <= self.big_c.initial_price_rounded):
        #     logger.info("justice! no under initial")
        #     return self
        if self.big_c.total_holding == 0:
            logger.info("forget it")
            return self._transact(IgnoreStrategy)
        return self

    def output(self):
        if not self.big_c.bids:
            self._fast_forward()
        self._output_balanced()
