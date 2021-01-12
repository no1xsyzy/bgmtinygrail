from datetime import datetime
from typing import List

from click.utils import LazyFile

from ._helpers import Targets
from ..tinygrail import Player


def level_colors(level: int) -> str: ...


def time_color(end_date: datetime) -> str: ...


def fall_to_met(value: float) -> str: ...


def _check_current(parsed_targets: Targets, player: Player, show_exceeds: bool, show_on_market: bool): ...


def check_targets(player: Player, targets: List[str], from_file: List[LazyFile], output_format: str,
                  show_exceeds: bool, show_initials: bool, show_on_market: bool, show_targets: bool) -> None: ...
