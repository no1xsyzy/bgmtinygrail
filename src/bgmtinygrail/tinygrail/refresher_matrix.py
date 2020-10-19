from collections import defaultdict
from datetime import datetime, timedelta
from typing import *
from weakref import WeakMethod

Refresher = Callable[[], Any]
Token = str


class InvalidRefreshToken(ValueError):
    pass


class RefreshMatrix:
    tokens: Set[Token]
    last_refresh: DefaultDict[Token, Optional[datetime]]
    interval: DefaultDict[Token, Optional[timedelta]]
    refresher_pairs: List[Tuple[Token, 'WeakMethod[Refresher]']]

    def __init__(self, tokens: List[str], *,
                 default_interval: timedelta = timedelta(2),
                 allow_new_token_on_register: bool = False):
        self.tokens = set(tokens)
        self.last_refresh = defaultdict(lambda: None)
        self.interval = defaultdict(lambda: default_interval)
        self.refresher_pairs = []
        self.allow_new_token_on_register = allow_new_token_on_register

    def more_tokens(self, *tokens):
        self.tokens.update(tokens)

    def register_refresher(self, token: Token, func: Refresher):
        if token not in self.tokens:
            if self.allow_new_token_on_register:
                self.tokens.add(token)
            else:
                raise InvalidRefreshToken(f"Token `{token}` is not a registered token")
        self.refresher_pairs.append((token, WeakMethod(func)))

    def batch_register(self, batches: List[Tuple[Token, Refresher]]):
        for token, func in batches:
            self.register_refresher(token, func)

    def refreshes(self, *tokens: Token):
        for token in tokens:
            last_refresh = self.last_refresh.get(token, None)
            interval = self.interval.get(token, None)
            if last_refresh is None or (interval is not None
                                        and last_refresh + interval < datetime.now()):
                refreshers: List[Refresher] = [wfr() for tok, wfr in self.refresher_pairs
                                               if tok == token and wfr() is not None]
                if not refreshers:
                    raise InvalidRefreshToken(f"Token `{token}` does not have a refresher")
                refresher = refreshers[0]
                refresher()
                for update_token, weak_func_ref in self.refresher_pairs:
                    if weak_func_ref() == refresher:
                        self.last_refresh[update_token] = datetime.now()

    def invalidates(self, *tokens):
        for token in tokens:
            self.last_refresh.pop(token, None)


class RefreshMatrixContained(Protocol):
    refresh_matrix: RefreshMatrix
