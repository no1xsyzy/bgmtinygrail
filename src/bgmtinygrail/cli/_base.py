import click

from ..tinygrail.player import Player


class TGPlayerParamType(click.ParamType):
    name = "tg_player"

    def convert(self, value, param, ctx):
        try:
            from ..db import accounts
            acc = accounts.retrieve(value)
            return Player(acc.tinygrail_identity)
        except IndexError:
            self.fail(f"no such player {value!r}", param, ctx)


TG_PLAYER = TGPlayerParamType()
