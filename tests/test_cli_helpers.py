# noinspection PyProtectedMember
from bgmtinygrail.cli._helpers import parse_target


class TestParseTarget:
    def test_empty_target(self):
        assert parse_target([]) == {}

    def test_simple_target(self):
        assert parse_target(["1=2/3"]) == {1: (2, 3)}

    def test_multiple_target(self):
        assert parse_target(["1=2/3", "4=5/6"]) == {1: (2, 3), 4: (5, 6)}

    def test_suppress_hold(self):
        assert parse_target(["1=2/"]) == {1: (2, 0)}

    def test_suppress_hold_and_slash(self):
        assert parse_target(["1=2"]) == {1: (2, 0)}

    def test_suppress_tower(self):
        assert parse_target(["1=/2"]) == {1: (0, 2)}

    def test_cv(self):
        result = parse_target(["cv/4353=1/2"])
        assert len(result) == 58
        assert all(v == (1, 2) for v in result.values())
