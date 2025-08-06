from __future__ import annotations

import click
from typing import Iterable, Mapping, Optional


class MonoHighlighter:
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

    def colorize_lines(
        self,
        text: str
    ) -> str:
        """
        Принять цельный текст, разбить его на строки (с сохранением \n/\r\n),
        раскрасить каждую строку и вернуть цельный раскрашенный текст.
        """
        parts: list[str] = []
        for chunk in text.splitlines(keepends=True):
            # Отделяем содержимое строки от переводов
            content_no_eol = chunk.rstrip("\r\n")
            eol = chunk[len(content_no_eol):]  # то, что срезали — это \r, \n или \r\n
            colored = self.colorize_line(content_no_eol)
            parts.append(colored + eol)

        # Если текст не заканчивался переводом строки, splitlines(keepends=True)
        # вернёт последнюю "строку" без \n — выше это уже учтено.
        if not parts and text == "":
            return ""

        return "".join(parts)
