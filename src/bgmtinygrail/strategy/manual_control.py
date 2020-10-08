from ._base import *


class ManualControlStrategy(ABCCharaStrategy):
    strategy = Strategy.MANUAL_CONTROL

    def transition(self):
        return self

    def output(self):
        pass
