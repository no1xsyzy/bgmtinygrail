from ._base import *


class FundamentalTrader(ABCTrader):
    internal_rate: float

    def __init__(self, player):
        super().__init__(player)
        self.update_internal_rate()

    def update_internal_rate(self):
        self.internal_rate = 0.1

    def tick(self, cid):
        big_c = self.big_c(cid)
        exchange_price = self._exchange_price(cid)
        if big_c.asks:  # selling, already in balance
            if big_c.amount > 0:
                logger.info("there is some part not selling")
                if not big_c.bids:
                    logger.info("and bids not existing")
                    self._fast_forward(cid, exchange_price)
                self._output_balanced(cid)
            elif big_c.asks[0].price != exchange_price:
                logger.info(f"exchange price not match ({big_c.asks[0].price} != {exchange_price})")
                self._output_balanced(cid)
            # otherwise, it must be unchanged
        elif big_c.amount > 0:
            logger.info("new stock")
            self._fast_seller(cid, low=self._exchange_price(cid))
            if big_c.amount or big_c.asks:
                self._output_balanced(cid)
        elif big_c.bids:
            if big_c.bids[0].price == 2.0 and big_c.bids[0].amount == 2:
                logger.info("forced view")
                self._fast_forward(cid, self._exchange_price(cid))
                self._output_balanced(cid)
            elif max(bid.price for bid in big_c.bids_all) <= big_c.initial_price_rounded:
                logger.info("justice! no under initial")
                self._output_balanced(cid)
            else:
                logger.info("forget it")
                big_c.ensure_bids([])
        # otherwise nothing

    def _exchange_price(self, cid):
        big_c = self.big_c(cid)
        return max([big_c.initial_price_rounded, self._fundamental(cid)])

    def _fundamental(self, cid):
        big_c = self.big_c(cid)
        return round(big_c.rate / self.internal_rate, 2)

    def _fast_forward(self, cid, price=None):
        logger.debug(f"fast forward #{cid:<5} | {price}")
        big_c = self.big_c(cid)
        price = price or self._exchange_price(cid)
        amount = 100
        big_c.ensure_bids([])
        big_c.update_user_character(ignore_throttle=True)
        while not big_c.bids:
            big_c.ensure_bids([TBid(Price=price, Amount=amount)])
            big_c.update_user_character(ignore_throttle=True)
            amount *= 2
        big_c.ensure_bids([TBid(Price=price, Amount=100)])
        big_c.update_user_character(ignore_throttle=True)

    def _fast_seller(self, cid, amount=None, low=10, high=100000):
        logger.debug(f"fast seller #{cid:<5} | ({low}-{high}) / {amount}")
        big_c = self.big_c(cid)
        big_c.ensure_bids([], force_updates='before')
        big_c.ensure_asks([], force_updates='after')
        if amount is None:
            amount = big_c.amount
        while amount:
            pin = round(0.618 * high + 0.382 * low, 2)
            if pin == high or pin == low:
                break
            big_c.ensure_asks([TAsk(Price=pin, Amount=1)], force_updates='after')
            if big_c.asks:
                big_c.ensure_asks([], force_updates='after')
                high = pin
            else:
                low = pin
                amount -= 1
        if amount:
            big_c.ensure_asks([TAsk(Price=low, Amount=amount)], force_updates='after')

    def _output_balanced(self, cid):
        exchange_price = self._exchange_price(cid)
        logger.debug(f"output balanced #{cid:<5} | {exchange_price}")
        big_c = self.big_c(cid)
        big_c.update_user_character(ignore_throttle=True)
        if big_c.total_holding:
            big_c.ensure_asks([TAsk(Price=exchange_price, Amount=big_c.total_holding)])
        big_c.ensure_bids([TBid(Price=exchange_price, Amount=100)], force_updates='after')
