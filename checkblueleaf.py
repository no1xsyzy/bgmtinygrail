#!/usr/bin/env python3
import functools
from random import choice

from accounts import *
from tinygrail.api import *


@functools.lru_cache(maxsize=1000)
def all_bl_char():
    return blueleaf_chara_all(no1xsyzy)


depth = functools.lru_cache(maxsize=1000)(depth)


get_init_cost = functools.lru_cache(maxsize=10000)(get_initial_price)


def sim_sell(cid, amount):
    bids = depth(cid).bids
    init_cost = get_init_cost(cid)
    sell_blueleaf_price = 0.8 * init_cost
    rev = 0
    for bid in sorted((bid for bid in bids if bid.price > sell_blueleaf_price),
                      key=lambda b: b.price, reverse=True):
        if bid.amount >= amount:
            rev += amount * bid.price
            return rev
        amount -= bid.amount
        rev += bid.amount * bid.price
    rev += amount*sell_blueleaf_price
    return rev


def monte_carlo_one_run():
    total = 100
    rev = 0
    s = []
    while total > 0:
        chara = choice(all_bl_char())
        cid = chara.id
        amount = choice(range(min([
            total,
            chara.state
        ]))) + 1
        rev += sim_sell(cid, amount)
        s.append((chara.name, amount))
        total -= amount
    return rev, s


def monte_carlo(times):
    result = []
    for i in range(times):
        rev, lst = monte_carlo_one_run()
        result.append(rev)
        print(f"{i:5}:: {rev:5.2f}: {lst}")
    return result


def violin(data):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.violinplot(data, showmeans=True)
    plt.show()


if __name__ == "__main__":
    j = monte_carlo(1000)
    violin(j)
