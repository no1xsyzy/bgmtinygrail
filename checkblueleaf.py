#!/usr/bin/env python3
from tinygrail.api import *
from random import choice
import functools


@functools.lru_cache(maxsize=1000)
def allc():
    return blueleaf_chara_all().value.items


depth = functools.lru_cache(maxsize=1000)(depth)


@functools.lru_cache(maxsize=1000)
def get_init_cost(cid):
    return chara_charts(cid).Value[0].begin


def trysell(cid, amount):
    bids = depth(cid).value.bids
    init_cost = get_init_cost(cid)
    sell_blueleaf_price = 0.8 * init_cost
    rev = 0
    for bid in sorted((bid for bid in bids if bid.price > sell_blueleaf_price),
                      key=lambda bid: bid.Price, reverse=True):
        if bid.amount >= amount:
            rev += amount*bid.price
            return rev
        amount -= bid.amount
        rev += bid.amount * bid.price
    rev += amount*sell_blueleaf_price
    return rev


def montecarlo_once():
    total = 100
    rev = 0
    s = []
    while total > 0:
        chara = choice(allc())
        cid = chara.Id
        amount = choice(range(min([
            total,
            chara.State
        ])))+1
        rev += trysell(cid, amount)
        s.append((chara.Name, amount))
        total -= amount
    return rev, s


def montecarlo_list(times):
    result = []
    for i in range(times):
        rev, lst = montecarlo_once()
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
    j = montecarlo_list(1000)
    violin(j)
