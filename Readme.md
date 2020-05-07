# bgmtinygrail

Consists two modules do deal <bgm.tv> and TinyGrail.

## Basic Usage

```python
# accounts.py
from bgmd.model import Login
from bgmd.api import user_info
from tinygrail.model import Player

bgm_xsb_player = Login(
    cfduid='123456abcdef',  # bgm.tv cookie `__cfduid'
    chii_auth='abcdefg',    # bgm.tv cookie `chii_auth'
    gh='abcdefg',           # see any character page and see collect button URL `gh' params
    user=user_info(525688)  # uid or username
)

tinygrail_xsb_player = Player('CfDJ8....')  # tinygrail.com cookie `.AspNetCore.Identity.Application'
```
