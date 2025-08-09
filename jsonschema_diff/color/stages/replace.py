from __future__ import annotations

import re
import difflib
from typing import Optional

from rich.console import Console
from rich.style import Style
from rich.text import Text

from ..abstraction import LineHighlighter


class ReplaceGenericHighlighter(LineHighlighter):
    """
    Универсальная подсветка replace-строк формата:
        '…: OLD -> NEW'
    Правила:
      • парсим только хвост ПОСЛЕ ПЕРВОГО ':' в строке;
      • diff по символьно через difflib.SequenceMatcher;
      • подсвечиваем фоном ТОЛЬКО отличия (OLD: replace/delete, NEW: replace/insert);
      • уже существующие стили (цвет/жирность) сохраняются.

    Параметры:
      bg_color         — цвет фона для отличий (любой цвет rich: 'grey35', 'bright_black', '#eef3ff', …)
      arrow_color      — цвет для стрелки '->' (None = не трогать)
      case_sensitive   — учитывать регистр при сравнении
      underline_changes— подчёркивать отличия
    """

    _TAIL_PATTERN = re.compile(
        r'(?P<left_ws>\s*)'
        r'(?P<old>.*?)'
        r'(?P<between_ws>\s*)'
        r'(?P<arrow>->)'
        r'(?P<right_ws>\s*)'
        r'(?P<new>.*?)'
        r'(?P<trailing_ws>\s*)$'
    )

    def __init__(
        self,
        *,
        bg_color: str = "grey35",
        arrow_color: Optional[str] = None,
        case_sensitive: bool = True,
        underline_changes: bool = False,
    ) -> None:
        self.bg_color = bg_color
        self.arrow_color = arrow_color
        self.case_sensitive = case_sensitive
        self.underline_changes = underline_changes

        self._console = Console(force_terminal=True, color_system="truecolor", width=10_000)
        self._bg_style = Style(bgcolor=self.bg_color, underline=self.underline_changes)
        self._arrow_style = Style(color=self.arrow_color) if self.arrow_color else None

    # -- публичный API --------------------------------------------------------

    def colorize_line(self, line: str) -> str:
        # 1) разбираем уже раскрашенную ANSI-строку в rich.Text
        text = Text.from_ansi(line)
        plain = text.plain

        # 2) ищем ПЕРВЫЙ ':' и работаем только с хвостом
        colon_idx = plain.find(":")
        if colon_idx == -1:
            return line

        head_plain = plain[: colon_idx + 1]
        tail_plain = plain[colon_idx + 1 :]

        tail_match = self._TAIL_PATTERN.match(tail_plain)
        if not tail_match:
            return line

        # 3) извлекаем куски хвоста
        left_ws = tail_match.group("left_ws")
        old_text = tail_match.group("old")
        between_ws = tail_match.group("between_ws")
        arrow = tail_match.group("arrow")
        right_ws = tail_match.group("right_ws")
        new_text = tail_match.group("new")
        trailing_ws = tail_match.group("trailing_ws")

        # 4) считаем абсолютные позиции OLD/NEW в plain-строке
        base = len(head_plain)
        old_start = base + len(left_ws)
        old_end = old_start + len(old_text)

        arrow_start = old_end + len(between_ws)
        arrow_end = arrow_start + len(arrow)

        new_start = arrow_end + len(right_ws)
        new_end = new_start + len(new_text)

        # 5) строим посимвольный diff на plain-тексте
        a_cmp = old_text if self.case_sensitive else old_text.lower()
        b_cmp = new_text if self.case_sensitive else new_text.lower()
        opcodes = difflib.SequenceMatcher(a=a_cmp, b=b_cmp).get_opcodes()

        # OLD: replace/delete
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "delete") and i1 != i2:
                text.stylize(self._bg_style, old_start + i1, old_start + i2)

        # NEW: replace/insert
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "insert") and j1 != j2:
                text.stylize(self._bg_style, new_start + j1, new_start + j2)

        # 6) при желании перекрасим стрелку
        if self._arrow_style:
            text.stylize(self._arrow_style, arrow_start, arrow_end)

        # 7) отдаём готовую ANSI-строку
        return self._render(text)

    def colorize_lines(self, text: str) -> str:
        parts: list[str] = []
        for chunk in text.splitlines(keepends=True):
            line = chunk.rstrip("\r\n")
            eol = chunk[len(line) :]
            parts.append(self.colorize_line(line) + eol)
        return "".join(parts)

    # -- внутреннее -----------------------------------------------------------

    def _render(self, t: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(t, end="")
        return cap.get()
