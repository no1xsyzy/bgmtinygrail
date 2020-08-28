from typing import *

from tinygrail.api import scratch_bonus2, scratch_gensokyo
from .fundamentally import *

scratch_translate = {
    'bonus2': scratch_bonus2,
    'gensokyo': scratch_gensokyo,
}


class GracefulTrader(FundamentalTrader):
    fixed: List[int]

    def __init__(self, player):
        super().__init__(player)
        self.init_fixed()

    def init_fixed(self):
        self.fixed = []

    def daily_bonus(self, rule: Optional[Tuple[str, Union[Literal['inf'], int]]] = None):
        if rule is None:
            rule = ('bonus2', 'inf'),
        results = {}
        for scratch_type, times in rule:
            if isinstance(times, int):
                iterable = range(times)
            else:
                assert times == 'inf'
                import itertools
                iterable = itertools.count()
            for t in iterable:
                for sb in scratch_translate[scratch_type](self.player):
                    logger.debug(f"scratch_{scratch_type:<10} | "
                                 f"got #{sb.id:<5} {sb.amount} stock, with highest price {sb.sell_price}")
                    results[sb.id] = sb.sell_price
        for cid, sell_price in results.items():
            big_c = self.big_c(cid)
            if big_c.asks or sell_price < big_c.initial_price_rounded:
                self.tick(cid)
                continue
            big_c.create_ask(TAsk(Price=sell_price, Amount=big_c.amount), force_updates=True)
            if big_c.asks:
                big_c.ensure_asks([], force_updates=True)
                self._fast_seller(cid, big_c.amount, low=big_c.initial_price_rounded, high=sell_price)