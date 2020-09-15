#!/usr/bin/env python3
import sys

from accounts import *
from data import *
from tinygrail.api import *

fn = None

if len(sys.argv) < 2:
    fn = "follow.txt"
elif sys.argv[1] == '-f' or sys.argv[1] == '--file':
    fn = sys.argv[2]
elif sys.argv[1].startswith("--file="):
    fn = sys.argv[1][len("--file="):]

if fn is None:
    lst = [int(arg) for arg in sys.argv[1:]]
else:
    lst = loadlines(fn, factory=int)

for chara in lst:
    name = character_info(no1xsyzy, chara).name
    hbid = depth(no1xsyzy, chara).highest_bid
    mybids = user_character(no1xsyzy, chara).bids
    if not mybids:
        print(f"https://bgm.tv/character/{chara:<5}   not buying? {name}")
        continue
    myhbid = mybids[0]
    if hbid.price - myhbid.price >= 0.01:
        print(f"https://bgm.tv/character/{chara:<5}   higher      {name}")
    elif myhbid.amount < 90:
        print(f"https://bgm.tv/character/{chara:<5}   refuel      {name}")
    elif hbid.amount - myhbid.amount > 50:
        pass
