# jsonschema_diff/color/replace_generic_stage_rich.py
from __future__ import annotations

import re, difflib
from typing import Tuple
from rich.console import Console
from rich.text import Text
from rich.style import Style

from ..abstraction import LineHighlighter

# простая ANSI палитра для осветления базового цвета
ANSI_RGB = {
    "black": (0,0,0), "red": (205,0,0), "green": (0,205,0), "yellow": (205,205,0),
    "blue": (0,0,205), "magenta": (205,0,205), "cyan": (0,205,205), "white": (229,229,229),
    "bright_black": (127,127,127), "bright_red": (255,85,85), "bright_green": (85,255,85),
    "bright_yellow": (255,255,85), "bright_blue": (85,85,255), "bright_magenta": (255,85,255),
    "bright_cyan": (85,255,255), "bright_white": (255,255,255),
}

def _clamp01(x: float) -> float: return 0.0 if x < 0 else 1.0 if x > 1 else x
def _lighten_hex(rgb: Tuple[int,int,int], pct: float) -> str:
    pct = _clamp01(pct)
    r,g,b = rgb
    lr = int(r + (255 - r) * pct)
    lg = int(g + (255 - g) * pct)
    lb = int(b + (255 - b) * pct)
    return f"#{lr:02x}{lg:02x}{lb:02x}"

class ReplaceGenericHighlighter(LineHighlighter):
    """
    Универсальная подсветка replace: '…: OLD -> NEW'
    - режем по ПЕРВОМУ ':' и диффим только хвост;
    - difflib.SequenceMatcher (pos-точные opcodes);
    - меняем ТОЛЬКО фон у отличий, остальное не трогаем;
    - ANSI-safe: работаем с rich.Text.from_ansi и индексами plain-текста.
    """

    # разбор хвоста после первого ':'
    _re_tail = re.compile(
        r'(?P<lws>\s*)'
        r'(?P<old>.*?)'
        r'(?P<mws>\s*)'
        r'(?P<arrow>->)'
        r'(?P<nws>\s*)'
        r'(?P<new>.*?)'
        r'(?P<ews>\s*)$'
    )

    def __init__(
        self,
        *,
        base_fg: str = "cyan",      # цвет текста дифф-сегментов (если его нет ранее)
        lighten_pct: float = 0.28,   # 0..1 — насколько осветлить фон от base_fg
        case_sensitive: bool = True,
        underline_changes: bool = False,
    ) -> None:
        self.base_fg = base_fg
        self.lighten_pct = lighten_pct
        self.case_sensitive = case_sensitive
        self.underline_changes = underline_changes
        self._console = Console(force_terminal=True, color_system="truecolor", width=10_000)

        rgb = ANSI_RGB.get(base_fg.lower(), (0, 205, 205))  # по умолчанию cyan
        self._bg_hex = _lighten_hex(rgb, lighten_pct)
        # стиль фона “поверх” существующих стилей
        self._bg_style = Style(bgcolor=self._bg_hex, underline=self.underline_changes)
        self._fg_style = Style(color=self.base_fg)  # на всякий случай для стрелки/если нужно

    def _render(self, t: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(t, end="")
        return cap.get()

    def colorize_line(self, line: str) -> str:
        # парсим вход как ANSI → Text (с уже существующими стилями)
        t = Text.from_ansi(line)
        plain = t.plain

        # строго по ПЕРВОМУ ':'
        colon = plain.find(':')
        if colon == -1:
            return line

        head_plain = plain[:colon+1]
        tail_plain = plain[colon+1:]

        m = self._re_tail.match(tail_plain)
        if not m:
            return line

        lws  = m.group("lws")
        old_txt = m.group("old")
        mws  = m.group("mws")
        arrow = m.group("arrow")  # '->'
        nws  = m.group("nws")
        new_txt = m.group("new")
        ews  = m.group("ews")

        # вычислим абсолютные позиции подстрок в plain-строке
        offset = len(head_plain)
        o_start = offset + len(lws)
        o_end   = o_start + len(old_txt)
        n_start = o_end + len(mws) + len(arrow) + len(nws)
        n_end   = n_start + len(new_txt)

        # посимвольный diff по old/new (с учётом регистра, если нужно)
        a = old_txt if self.case_sensitive else old_txt.lower()
        b = new_txt if self.case_sensitive else new_txt.lower()
        sm = difflib.SequenceMatcher(a=a, b=b)
        opcodes = sm.get_opcodes()

        # Подсветка в OLD: replace/delete
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "delete") and i1 != i2:
                t.stylize(self._bg_style, o_start + i1, o_start + i2)

        # Подсветка в NEW: replace/insert
        for tag, i1, i2, j1, j2 in opcodes:
            if tag in ("replace", "insert") and j1 != j2:
                t.stylize(self._bg_style, n_start + j1, n_start + j2)

        # (опционально) перерисовать стрелку базовым цветом
        arrow_pos = o_end + len(mws)
        t.stylize(self._fg_style, arrow_pos, arrow_pos + len(arrow))

        return self._render(t)
