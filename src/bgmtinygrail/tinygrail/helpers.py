"""pure functions for calculating"""


def ico_minimal_investment_for_level(level):
    investment = 0
    for i in range(1, level + 1):
        investment += i * i * 100000
    return investment


def ico_minimal_investors_for_level(level):
    return level * 5 + 10


def ico_now_level_by_investment(total_investment):
    import itertools
    for i in itertools.count(1):
        total_investment -= i * i * 100000
        if total_investment < 0:
            return i - 1


def ico_now_level_by_investors(total_investors):
    return (total_investors - 10) // 5


def ico_now_level(total_investment, total_investors):
    for i in range(1, (total_investors - 10) // 5 + 1):
        total_investment -= i * i * 100000
        if total_investment < 0:
            return i - 1
    else:
        return (total_investors - 10) // 5


def ico_offerings_for_level(level):
    return level * 7500 + 2500
