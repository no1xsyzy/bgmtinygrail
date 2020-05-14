from dacite import from_dict
from typing import *
import re
import requests
from .model import *
from .helper import *
import logging

logger = logging.getLogger('bgmd.api')

__all__ = ['user_info', 'user_mono', 'person_work_voice_character', 'collect_mono', 'erase_collect_mono']

empty_session = requests.Session()

empty_session.cookies['__cfduid'] = 'd633ed72fd4689407e7db8efc96eb92411588180481'
empty_session.cookies['chii_theme'] = 'light'
empty_session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'


def user_info(uid: Optional[int] = None, username: Optional[str] = None) -> User:
    """Usage: ``user_info(123456) or user_info(username='no1xsyzy')``. Returns :class:`User` object."""
    return from_dict(User, empty_session.get(f"https://api.bgm.tv/user/{uid or username}").json())


def user_mono(user: User, monotype: Literal['both', 'character', 'person']) -> List[Union[Character, Person]]:
    assert monotype in {'both', 'character', 'person'}, ValueError
    if monotype == 'both':
        return user_mono(user, 'character') + user_mono(user, 'person')
    response = empty_session.get(f"https://bgm.tv/user/{user.username}/mono/{monotype}")
    result, all_pages = crop_mono(response.content)
    for page in range(2, all_pages+1):
        response = empty_session.get(f"https://bgm.tv/user/{user.username}/mono/{monotype}?page={page}")
        content = response.content
        res_ext, _ = crop_mono(content)
        result.extend(res_ext)
    return [Character(int(c.split("/")[-1])) for c in result]


def person_work_voice_character(person: Person) -> List[Character]:
    response = empty_session.get(f"https://bgm.tv/person/{person.id}/works/voice")
    soup = BeautifulSoup(response.content, 'html.parser')
    characters = [int(k[0])
                  for k in (re.findall(r"/character/(\d+)", m)
                            for m in (a['href']
                                      for a in soup.find_all("a", {"class": "l"})))
                  if k]
    return [Character(cid) for cid in characters]


def collect_mono(login: Login, character: Union[Character, int]):
    if isinstance(character, Character):
        cid = character.id
    else:
        cid = character
    logger.info(f"collecting character: {cid}")
    response = login.session.get(f"https://bgm.tv/character/{cid}/collect?gh={login.gh}", allow_redirects=False)
    logger.debug(f"{response.status_code=}, {response.headers['Location']=}")
    successful = response.status_code == 302 and response.headers['Location'].startswith('/character/')
    if successful:
        logger.info(f"Collected character: {cid}")
    else:
        logger.error(f"Failed in collecting character: {cid}")
    return successful


def erase_collect_mono(login: Login, character: Union[Character, int]):
    if isinstance(character, Character):
        cid = character.id
    else:
        cid = character
    logger.info(f"removing collected character: {cid}")
    response = login.session.get(f"https://bgm.tv/character/{cid}/erase_collect?gh={login.gh}", allow_redirects=False)
    logger.debug(f"{response.status_code=}, {response.headers['Location']=}")
    successful = response.status_code == 302 and response.headers['Location'].startswith('/character/')
    if successful:
        logger.info(f"Removed collection: {cid}")
    else:
        logger.error(f"Failed in removing collection: {cid}")
    return successful
