from ._base import *


class SelfServiceStrategy(ABCCharaStrategy):
    strategy = Strategy.SELF_SERVICE

    def transition(self):
        return self

    def output(self):
        pass
