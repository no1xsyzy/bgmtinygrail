import pytest
from pytest_mock import MockerFixture

from bgmtinygrail.bgmd.api import *
from bgmtinygrail.bgmd.model import *

user = user_info(525688)


class TestUserInfo:
    def test_user_info(self):
        assert user.id == 525688
        assert user.url == "http://bgm.tv/user/525688"
        assert user.username == '525688'
        assert user.nickname == "小圣杯玩家"


class TestUserMono:
    def test_character(self):
        result = user_mono(user, 'character')
        assert len(result) == 64
        assert isinstance(result[0], Character) and result[0].id == 65
        assert isinstance(result[-1], Character) and result[-1].id == 1
        assert 56 not in {c.id for c in result}  # Character(id=56) doesn't exists

    def test_person(self):
        result = user_mono(user, 'person')
        assert len(result) == 65
        assert isinstance(result[0], Person) and result[0].id == 65
        assert isinstance(result[-1], Person) and result[-1].id == 1

    def test_both(self):
        result = user_mono(user, 'both')
        assert len(result) == 129
        assert isinstance(result[0], Character) and result[0].id == 65
        assert isinstance(result[63], Character) and result[63].id == 1
        assert isinstance(result[64], Person) and result[64].id == 65
        assert isinstance(result[-1], Person) and result[-1].id == 1
        assert (Character, 56) not in {(type(c), c.id) for c in result}

    def test_wrong(self):
        with pytest.raises(AssertionError) as exc_info:
            # noinspection PyTypeChecker
            # testing with wrong type
            result = user_mono(user, 'wrong')
        assert exc_info.value.args == ('no available mono type',)


class TestPersonWorkVoiceCharacter:
    def test_matsuki_miyu(self):
        result = person_work_voice_character(Person(id=4353))
        assert len(result) == 58
        assert isinstance(result[0], Character) and result[0].id == 15542
        assert isinstance(result[-1], Character) and result[-1].id == 88529


class TestCollectMono:
    def test_calls_with_cid(self, mocker: MockerFixture):
        from bgmtinygrail.bgmd.login import Login
        import requests
        from requests.structures import CaseInsensitiveDict

        login = Login(chii_auth='chii_auth', ua='ua', gh='gh')

        response = requests.Response()
        response.status_code = 302
        response.headers = CaseInsensitiveDict({'location': '/character/42'})

        mocked_get = mocker.patch.object(login.session, 'get')
        mocked_get.return_value = response
        assert collect_mono(login, 42) is True
        mocked_get.assert_called_once_with("https://bgm.tv/character/42/collect?gh=gh", allow_redirects=False)

    def test_calls_with_character(self, mocker: MockerFixture):
        from bgmtinygrail.bgmd.login import Login
        import requests
        from requests.structures import CaseInsensitiveDict

        login = Login(chii_auth='chii_auth', ua='ua', gh='gh')

        response = requests.Response()
        response.status_code = 302
        response.headers = CaseInsensitiveDict({'location': '/character/42'})

        mocked_get = mocker.patch.object(login.session, 'get')
        mocked_get.return_value = response
        assert collect_mono(login, Character(id=42)) is True
        mocked_get.assert_called_once_with("https://bgm.tv/character/42/collect?gh=gh", allow_redirects=False)

    def test_remote_changes(self):
        pytest.skip("Test user not implemented now")


class TestEraseCollectMono:
    def test_calls_with_cid(self, mocker: MockerFixture):
        from bgmtinygrail.bgmd.login import Login
        import requests
        from requests.structures import CaseInsensitiveDict

        login = Login(chii_auth='chii_auth', ua='ua', gh='gh')

        response = requests.Response()
        response.status_code = 302
        response.headers = CaseInsensitiveDict({'location': '/character/42'})

        mocked_get = mocker.patch.object(login.session, 'get')
        mocked_get.return_value = response
        assert erase_collect_mono(login, 42) is True
        mocked_get.assert_called_once_with("https://bgm.tv/character/42/erase_collect?gh=gh", allow_redirects=False)

    def test_calls_with_character(self, mocker: MockerFixture):
        from bgmtinygrail.bgmd.login import Login
        import requests
        from requests.structures import CaseInsensitiveDict

        login = Login(chii_auth='chii_auth', ua='ua', gh='gh')

        response = requests.Response()
        response.status_code = 302
        response.headers = CaseInsensitiveDict({'location': '/character/42'})

        mocked_get = mocker.patch.object(login.session, 'get')
        mocked_get.return_value = response
        assert erase_collect_mono(login, Character(id=42)) is True
        mocked_get.assert_called_once_with("https://bgm.tv/character/42/erase_collect?gh=gh", allow_redirects=False)

    def test_remote_changes(self):
        pytest.skip("Test user not implemented now")


class TestCharacterCollection:
    def test_shokuhou_misaki_call_with_cid(self):
        assert '/user/no1xsyzy' in character_collection(17949)

    def test_yonomori_kobeni_call_with_character(self):
        assert '/user/no1xsyzy' in character_collection(Character(id=21418))
