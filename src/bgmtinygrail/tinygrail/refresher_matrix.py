from collections import defaultdict
from datetime import datetime, timedelta
from typing import *
from weakref import WeakSet, WeakKeyDictionary

Refresher = Callable[[], Any]
Token = str


class InvalidRefreshToken(ValueError):
    pass


class RefreshMatrix:
    tokens: Set[Token]
    last_refresh: DefaultDict[Token, Optional[datetime]]
    interval: DefaultDict[Token, Optional[timedelta]]
    token_refresher: DefaultDict[Token, 'WeakSet[Refresher]']
    refresher_refreshes: 'WeakKeyDictionary[Refresher, Set[Token]]'

    def __init__(self, tokens: List[str], *,
                 default_interval: timedelta = timedelta(2),
                 allow_new_token_on_register: bool = False):
        self.tokens = set(tokens)
        self.last_refresh = defaultdict(lambda: None)
        self.interval = defaultdict(lambda: default_interval)
        self.token_refresher = defaultdict(WeakSet)
        self.refresher_refreshes = WeakKeyDictionary()
        self.allow_new_token_on_register = allow_new_token_on_register

    def more_tokens(self, *tokens):
        self.tokens.update(tokens)

    def register_refresher(self, token: Token, func: Refresher):
        if token not in self.tokens:
            if self.allow_new_token_on_register:
                self.tokens.add(token)
            else:
                raise InvalidRefreshToken(f"Token `{token}` is not a registered token")
        self.token_refresher[token].add(func)
        self.refresher_refreshes.setdefault(func, set())
        self.refresher_refreshes[func].add(token)

    def batch_register(self, batches: List[Tuple[Token, Refresher]]):
        for token, func in batches:
            self.register_refresher(token, func)

    def refreshes(self, *tokens: Token):
        for token in tokens:
            last_refresh = self.last_refresh.get(token, None)
            interval = self.interval.get(token, None)
            if last_refresh is None or (interval is not None
                                        and last_refresh + interval < datetime.now()):
                if len(self.token_refresher[token]) == 0:
                    raise InvalidRefreshToken(f"Token `{token}` does not have a refresher")
                refresher = next(iter(self.token_refresher[token]))
                refresher()
                for update_token in self.refresher_refreshes.get(refresher, []):
                    self.last_refresh[update_token] = datetime.now()

    def invalidates(self, *tokens):
        for token in tokens:
            self.last_refresh.pop(token, None)


class RefreshMatrixContained(Protocol):
    refresh_matrix: RefreshMatrix
