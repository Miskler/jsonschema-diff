from __future__ import annotations

import re
import difflib
from typing import Optional, List, Tuple

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
      • дифф по ТОКЕНАМ (число — единый токен), через difflib.SequenceMatcher;
      • подсвечиваем фоном ТОЛЬКО отличия (OLD: replace/delete, NEW: replace/insert);
      • уже существующие стили (цвет/жирность) сохраняются.

    Параметры:
      bg_color         — цвет фона для отличий (любой цвет rich: 'grey35', 'bright_black', '#eef3ff', …)
      arrow_color      — цвет для стрелки '->' (None = не трогать)
      case_sensitive   — учитывать регистр при сравнении
      underline_changes— подчёркивать отличия
    """

    # Хвост после первого двоеточия:  left_ws  OLD  between_ws  ->  right_ws  NEW  trailing_ws
    _TAIL_PATTERN = re.compile(
        r'(?P<left_ws>\s*)'
        r'(?P<old>.*?)'
        r'(?P<between_ws>\s*)'
        r'(?P<arrow>->)'
        r'(?P<right_ws>\s*)'
        r'(?P<new>.*?)'
        r'(?P<trailing_ws>\s*)$'
    )

    # Токенизация:
    #  - числа (в т.ч. -12, 3.14, 5, ∞, допускаем "10px"/"50%" как единый числовой токен);
    #  - слова/идентификаторы;
    #  - пробелы;
    #  - одиночный символ (пунктуация, скобки, многоточия и т.п.).
    _TOKEN_RE = re.compile(
        r"""
        (?P<num>[+-]?\d+(?:[.,]\d+)?(?:[a-z%]+)?|∞)
      | (?P<word>\w+)
      | (?P<space>\s+)
      | (?P<punc>.)
        """,
        re.VERBOSE | re.UNICODE,
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

    # ------------------------- Публичный API ---------------------------------

    def colorize_line(self, line: str) -> str:
        """Принимает ANSI-строку, возвращает ANSI-строку с подсветкой отличий."""
        # 1) разбор уже раскрашенной ANSI-строки в rich.Text
        text = Text.from_ansi(line)
        plain = text.plain

        # 2) первый ':' — всё, что справа, считаем 'OLD -> NEW'
        colon_idx = plain.find(":")
        if colon_idx == -1:
            return line

        head_plain = plain[: colon_idx + 1]
        tail_plain = plain[colon_idx + 1 :]

        m = self._TAIL_PATTERN.match(tail_plain)
        if not m:
            return line

        # 3) куски хвоста
        left_ws = m.group("left_ws")
        old_text = m.group("old")
        between_ws = m.group("between_ws")
        arrow = m.group("arrow")
        right_ws = m.group("right_ws")
        new_text = m.group("new")
        trailing_ws = m.group("trailing_ws")

        # 4) абсолютные позиции OLD/NEW в plain-строке
        base = len(head_plain)
        old_start = base + len(left_ws)
        old_end = old_start + len(old_text)

        arrow_start = old_end + len(between_ws)
        arrow_end = arrow_start + len(arrow)

        new_start = arrow_end + len(right_ws)
        new_end = new_start + len(new_text)

        # 5) дифф по токенам (числа — атомарные)
        old_tokens = self._tokenize(old_text)
        new_tokens = self._tokenize(new_text)

        sm = difflib.SequenceMatcher(
            a=[t[3] for t in old_tokens],  # cmp-значения
            b=[t[3] for t in new_tokens],
        )
        opcodes = sm.get_opcodes()

        # OLD: replace/delete
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "delete"):
                span = self._span_from_tokens(old_tokens, i1, i2)
                if span:
                    s, e = span
                    text.stylize(self._bg_style, old_start + s, old_start + e)

        # NEW: replace/insert
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "insert"):
                span = self._span_from_tokens(new_tokens, j1, j2)
                if span:
                    s, e = span
                    text.stylize(self._bg_style, new_start + s, new_start + e)

        # 6) перекрас стрелки при необходимости
        if self._arrow_style:
            text.stylize(self._arrow_style, arrow_start, arrow_end)

        # 7) обратно в ANSI
        return self._render(text)

    # --------------------------- Внутреннее ----------------------------------

    def _tokenize(self, s: str) -> List[Tuple[str, int, int, str]]:
        """
        Возвращает список токенов: (raw_value, start, end, cmp_value)
        cmp_value — с учётом case_sensitive.
        """
        toks: List[Tuple[str, int, int, str]] = []
        for m in self._TOKEN_RE.finditer(s):
            val = m.group(0)
            cmpv = val if self.case_sensitive else val.lower()
            toks.append((val, m.start(), m.end(), cmpv))
        return toks

    @staticmethod
    def _span_from_tokens(tokens: List[Tuple[str, int, int, str]], i1: int, i2: int) -> Optional[Tuple[int, int]]:
        if i1 >= i2:
            return None
        return tokens[i1][1], tokens[i2 - 1][2]

    def _render(self, t: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(t, end="")
        return cap.get()
