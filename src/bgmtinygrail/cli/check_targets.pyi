from datetime import datetime
from typing import List

from click.utils import LazyFile

from ..tinygrail import Player


def level_colors(level: int) -> str: ...


def time_color(end_date: datetime) -> str: ...


def fall_to_met(value: float) -> str: ...


def colored_comparison(actual: int, target: int) -> str: ...


def check_targets(player: Player, targets: List[str], from_file: List[LazyFile],
                  show_exceeds: bool, output_format: str) -> None: ...
