from ._base import *


class ShowGraceStrategy(ABCCharaStrategy):
    strategy = Strategy.SHOW_GRACE

    def __post_init__(self):
        if 'sell_price' not in self.kwargs:
            raise ValueError("keyword argument required `sell_price`")

    @property
    def earned_value(self):
        return self.kwargs.get('earned_value', 0)

    @earned_value.setter
    def earned_value(self, value):
        self.kwargs['earned_value'] = value

    @property
    def sell_price(self):
        return self.kwargs.get('sell_price')

    def transition(self) -> 'ABCCharaStrategy':
        from strategy import BalanceStrategy, IgnoreStrategy
        logger.debug(f"grace #{self.cid:<5}, sell_price={self.sell_price}, amount={self.big_c.amount}")
        if self.big_c.asks or self.sell_price < self.big_c.initial_price_rounded:
            self.earned_value += self.big_c.fundamental_rounded * self.big_c.amount
            return self._transact(BalanceStrategy)
        self.big_c.create_ask(TAsk(Price=self.sell_price, Amount=self.big_c.amount), force_updates=True)
        if not self.big_c.asks:
            self.earned_value += self.sell_price * self.big_c.amount
            return self._transact(IgnoreStrategy)
        self._fast_seller(self.big_c.amount, low=self.big_c.initial_price_rounded, high=self.sell_price)
        if self.big_c.amount or self.big_c.asks:
            self.earned_value += self.big_c.fundamental_rounded * self.big_c.total_holding
            return self._transact(BalanceStrategy)

    def output(self):
        pass
