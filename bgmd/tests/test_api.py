import pytest
from bgmd.api import *
from bgmd.model import *

user = user_info(285822)


class TestUserInfo:
    def test_user_info(self):
        assert user.id == 285822
        assert user.url == 'http://bgm.tv/user/rog_defwang'
        assert user.username == 'rog_defwang'
        assert user.nickname == '凡付真遠'


class TestUserMono:
    def test_character(self):
        result = user_mono(user, 'character')
        assert len(result) == 1591
        assert isinstance(result[0], Character) and result[0].id == 76074
        assert isinstance(result[-1], Character) and result[-1].id == 36489

    def test_person(self):
        result = user_mono(user, 'person')
        assert len(result) == 298
        assert isinstance(result[0], Person) and result[0].id == 25428
        assert isinstance(result[-1], Person) and result[-1].id == 12507

    def test_both(self):
        result = user_mono(user, 'both')
        assert len(result) == 1889
        assert isinstance(result[0], Character) and result[0].id == 76074
        assert isinstance(result[1590], Character) and result[1590].id == 36489
        assert isinstance(result[1591], Person) and result[1591].id == 25428
        assert isinstance(result[-1], Person) and result[-1].id == 12507

    def test_wrong(self):
        with pytest.raises(AssertionError) as exc_info:
            # noinspection PyTypeChecker
            # testing with wrong type
            result = user_mono(user, 'wrong')
        assert exc_info.value.args == ('no available mono type',)


class TestPersonWorkVoiceCharacter:
    def test_matsuki_miyu(self):
        result = person_work_voice_character(Person(id=4353))
        assert len(result) == 57
        assert isinstance(result[0], Character) and result[0].id == 15542
        assert isinstance(result[-1], Character) and result[-1].id == 75791
