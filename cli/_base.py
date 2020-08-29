import click

from tinygrail.model import Player


class TGPlayerParamType(click.ParamType):
    name = "tg_player"

    def convert(self, value, param, ctx):
        try:
            from db import accounts
            dct = accounts.retrieve(value)[0]
            return Player(dct['tinygrail_identity'])
        except IndexError:
            self.fail(f"no such player {value!r}", param, ctx)


TG_PLAYER = TGPlayerParamType()
