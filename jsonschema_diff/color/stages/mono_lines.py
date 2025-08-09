from __future__ import annotations

import click
from typing import Mapping, Optional
from ..abstraction import LineHighlighter


class MonoLinesHighlighter(LineHighlighter):
    """
    Раскрашивает строки по правилам "начинается с -> цвет" (через click.style).
    Порядок перебора правил соответствует порядку в словаре.
    """
    def __init__(self,
                 bold: bool = False,
                 default_color: Optional[str] = None,
                 case_sensitive: bool = False,
                 rules: Mapping[str, str] = {
                     "-": "red",
                     "+": "green",
                     "r": "cyan",
                     "m": "cyan"
                 }) -> None:
        # Глобальный флаг "делать текст жирным"
        self.bold = bold
        self.default_color = default_color
        self.case_sensitive = case_sensitive
        self.rules = rules

    def colorize_line(
        self,
        line: str
    ) -> str:
        """
        Раскрасить одну строку по первому совпавшему префиксу.
        :param rules: {'ERROR': 'red', 'WARN': 'yellow', ...}
        :param default_color: цвет по умолчанию, если префиксы не совпали (None — без изменения).
        :param case_sensitive: учитывать регистр.
        """
        probe = line if self.case_sensitive else line.lower()

        for prefix, color in self.rules.items():
            pref = prefix if self.case_sensitive else prefix.lower()
            if probe.startswith(pref):
                return click.style(line, fg=color, bold=self.bold)

        if self.default_color is not None:
            return click.style(line, fg=self.default_color, bold=self.bold)
        if self.bold:
            return click.style(line, bold=True)
        return line
