#!/bin/sh
python -m bgmtinygrail check-cv 5076 --account no1xsyzy --target 0/2500,11614=0/0,56822=0/0

# Description:
# python -m cli check-cv               ---  The command it self
# 5076                                 ---  Yuuki Aoi is https://bgm.tv/person/5076
# --account no1xsyzy                   ---  Accounts added in `python -m cli accounts` command group
# --target 0/2500,11614=0/0,56822=0/0  ---  Define targets, splitted with comma `,`
# 0/2500                               ---  Default is a tower with 2500
# 11614=0/0                            ---  Ignores Konpaku Youmu, which is <https://bgm.tv/character/11614>
# 56822=0/0                            ---  Ignores Popuko, which is <https://bgm.tv/character/56822>
