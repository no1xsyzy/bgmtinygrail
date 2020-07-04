"""
Usage:
    magic.py chaos <username> <attacker_cid>
    magic.py guidepost <username> <attacker_cid> <target_cid>
"""
import sys
from pprint import pprint

import click

from tinygrail.api import magic_chaos, magic_guidepost, magic_stardust


class TGPlayerParamType(click.ParamType):
    name = "tg_player"

    def convert(self, value, param, ctx):
        try:
            import accounts
            return getattr(accounts, value)
        except ImportError:
            self.fail(f"you have not set up accounts.py correctly, see Readme.md")
        except SyntaxError:
            self.fail(f"your accounts.py has syntax error")
        except AttributeError:
            self.fail(f"no such player {value!r}", param, ctx)


TG_PLAYER = TGPlayerParamType()


@click.group()
def magic():
    """施放各类魔法

    在子命令中查看魔法的具体参数
    """


@magic.command()
@click.argument("player_name", type=TG_PLAYER, metavar="<玩家变量名>")
@click.argument("attacker_cid", type=int, metavar="<消耗角色圣殿>")
def chaos(player_name, attacker_cid):
    """施放混沌魔方"""
    result = magic_chaos(player_name, attacker_cid)
    pprint(result, stream=sys.stderr)
    return result


@magic.command()
@click.argument("player_name", type=TG_PLAYER, metavar="<玩家变量名>")
@click.argument("attacker_cid", type=int, metavar="<消耗角色圣殿>")
@click.argument("target_cid", type=int, metavar="<攻击目标角色>")
def guidepost(player_name, attacker_cid, target_cid):
    """施放虚空道标"""
    result = magic_guidepost(player_name, attacker_cid, target_cid)
    pprint(result, stream=sys.stderr)
    return result


@magic.command()
@click.argument("player_name", type=TG_PLAYER, metavar="<玩家变量名>")
@click.argument("supplier_cid", type=int, metavar="<能源>")
@click.argument("demand_cid", type=int, metavar="<目标>")
@click.argument("amount", type=int, metavar="<数量>")
@click.option('--temple', 'use_type', flag_value='temple', help="指定使用塔股")
@click.option('--position', 'use_type', flag_value='position', help="指定使用活股")
@click.option('--use-type', type=click.Choice(['position', 'temple'], case_sensitive=False),
              default='position', help="指定使用塔股或者活股")
def stardust(player_name, supplier_cid, demand_cid, amount, use_type):
    """施放星光碎片"""
    result = magic_stardust(player_name, supplier_cid, demand_cid, amount, use_type)
    pprint(result, stream=sys.stderr)
    return result


if __name__ == '__main__':
    magic()
