import pytest

from bgmtinygrail.tinygrail.helpers import *


class TestICOHelpers:
    def test_min_investment(self):
        with pytest.raises(ValueError):
            ico_minimal_investment_for_level(-1)
        with pytest.raises(ValueError):
            ico_minimal_investment_for_level(0)
        assert ico_minimal_investment_for_level(1) == 10_0000
        assert ico_minimal_investment_for_level(2) == 50_0000
        assert ico_minimal_investment_for_level(13) == 8190_0000

    def test_min_investors(self):
        with pytest.raises(ValueError):
            ico_minimal_investors_for_level(-1)
        with pytest.raises(ValueError):
            ico_minimal_investors_for_level(0)
        assert ico_minimal_investors_for_level(1) == 15
        assert ico_minimal_investors_for_level(2) == 20

    def test_now_level_calculator(self):
        assert ico_now_level_by_investors(14) == 0
        assert ico_now_level_by_investors(15) == 1
        assert ico_now_level_by_investors(19) == 1
        assert ico_now_level_by_investors(20) == 2
        assert ico_now_level_by_investment(9_9999) == 0
        assert ico_now_level_by_investment(10_0000) == 1
        assert ico_now_level_by_investment(49_9999) == 1
        assert ico_now_level_by_investment(50_0000) == 2
        assert ico_now_level(1e100, 15) == 1
        assert ico_now_level(10_0000, 1000000) == 1

    def ico_offerings_for_level(self):
        assert ico_offerings_for_level(1) == 1_0000
        assert ico_offerings_for_level(2) == 1_7500
        assert ico_offerings_for_level(13) == 10_0000
