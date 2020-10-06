from .fundamentally import *
from ..tinygrail.api import scratch_bonus2, scratch_gensokyo

scratch_translate = {
    'bonus2': scratch_bonus2,
    'gensokyo': scratch_gensokyo,
}


class GracefulTrader(FundamentalTrader):
    def graceful_tick(self, cid, sell_price):
        """indicated for daily bonus"""
        big_c = self.big_c(cid)
        if big_c.asks or sell_price < big_c.initial_price_rounded:
            self.tick(cid)
            return
        logger.debug(f"try sell all #{cid}, {sell_price=}, amount={big_c.amount}")
        big_c.create_ask(TAsk(Price=sell_price, Amount=big_c.amount), force_updates=True)
        if not big_c.asks:
            return
        self._fast_seller(cid, big_c.amount, low=big_c.initial_price_rounded, high=sell_price)
        if big_c.amount or big_c.asks:
            self._output_balanced(cid)
