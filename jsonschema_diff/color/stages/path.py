# jsonschema_diff/color/path_stage_rich.py
from __future__ import annotations

import re
from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.style import Style

from ..abstraction import LineHighlighter


class PathHighlighter(LineHighlighter):
    """
    Подсветка компонент пути, например:
      .$defs["item"]["blocks"][0]["type"].rangeLength
      ["tags"][0].rangeLength
      .range

    Правила:
      • '.' и '['/']' — base_color
      • "строки"/'строки' (включая кавычки) — string_color
      • числа — number_color
      • свойства после точки: все, кроме последнего — path_prop_color
      • последнее свойство (после последней точки) — prop_color (точка остаётся base_color)
    """

    # dot-свойства: .name  (JS-подобный идентификатор)
    _RE_DOT_PROP = re.compile(r"\.([A-Za-z_$][A-Za-z0-9_$]*)")
    # блоки в скобках: [ ... ] (без вложенности)
    _RE_BRACKET = re.compile(r"\[[^\]]*?\]")
    # строка в кавычках (простая версия, без экранирования)
    _RE_QUOTED_FULL = re.compile(r'^(?:"[^"]*"|\'[^\']*\')$')
    # число (возможен минус)
    _RE_NUMBER = re.compile(r"-?\d+")

    def __init__(
        self,
        *,
        base_color: str = "grey50",
        string_color: str = "yellow",
        number_color: str = "magenta",
        path_prop_color: str = "cyan",
        prop_color: str = "bright_cyan",
    ) -> None:
        self.base_style = Style(color=base_color)
        self.string_style = Style(color=string_color)
        self.number_style = Style(color=number_color)
        self.path_prop_style = Style(color=path_prop_color)
        self.prop_style = Style(color=prop_color)

        self._console = Console(force_terminal=True, color_system="truecolor", width=10_000)

    # ---------- public API ----------

    def colorize_line(self, line: str) -> str:
        # Разбираем ANSI → Text, чтобы наслаивать стили
        t = Text.from_ansi(line)
        plain = t.plain

        # Границы “пути”: от первого '.' или '[' до первого ':' (или конца строки)
        first_dot = plain.find(".")
        first_br = plain.find("[")
        candidates = [i for i in (first_dot, first_br) if i != -1]
        if not candidates:
            return line

        path_start = min(candidates)
        colon = plain.find(":")
        path_end = colon if colon != -1 else len(plain)
        if path_start >= path_end:
            return line

        # Локальный фрагмент plain для разбора
        segment = plain[path_start:path_end]

        # 1) Подсветка dot-свойств: найдём все, выделим последнее
        dot_props = list(self._RE_DOT_PROP.finditer(segment))
        last_prop_idx: Optional[int] = len(dot_props) - 1 if dot_props else None

        for idx, m in enumerate(dot_props):
            name_start_rel, name_end_rel = m.span(1)  # только имя
            dot_pos_rel = m.start()                   # позиция точки

            # точка — base
            t.stylize(self.base_style, path_start + dot_pos_rel, path_start + dot_pos_rel + 1)

            # имя свойства — либо промежуточное, либо финальное
            style = self.prop_style if (last_prop_idx is not None and idx == last_prop_idx) else self.path_prop_style
            t.stylize(style, path_start + name_start_rel, path_start + name_end_rel)

        # 2) Подсветка скобок и их содержимого
        for bm in self._RE_BRACKET.finditer(segment):
            br_s_rel, br_e_rel = bm.span()
            # '[' и ']' — base
            t.stylize(self.base_style, path_start + br_s_rel, path_start + br_s_rel + 1)
            t.stylize(self.base_style, path_start + br_e_rel - 1, path_start + br_e_rel)

            inner_start = br_s_rel + 1
            inner_end = br_e_rel - 1
            if inner_start >= inner_end:
                continue

            inner = segment[inner_start:inner_end].strip()
            # если весь контент — "строка" или 'строка', красим весь (включая кавычки)
            if self._RE_QUOTED_FULL.match(inner):
                # включительно с кавычками и внутренними символами
                t.stylize(self.string_style, path_start + inner_start, path_start + inner_end)
            else:
                # иначе — подсветим числа внутри
                for nm in self._RE_NUMBER.finditer(segment, inner_start, inner_end):
                    n_s_rel, n_e_rel = nm.span()
                    t.stylize(self.number_style, path_start + n_s_rel, path_start + n_e_rel)

        # 3) Точки, которые не попали в dot-проперти (например, одиночная ".range" без первых regex-совпадений)
        #    Уже покрыто _RE_DOT_PROP, но на всякий случай подсветим любые '.' в сегменте базовым цветом.
        for i, ch in enumerate(segment):
            if ch == ".":
                # избегаем двойного стилизования — это безопасно (rich их сольёт)
                t.stylize(self.base_style, path_start + i, path_start + i + 1)

        return self._render(t)

    def colorize_lines(self, text: str) -> str:
        parts: list[str] = []
        for chunk in text.splitlines(keepends=True):
            body = chunk.rstrip("\r\n")
            eol = chunk[len(body):]
            parts.append(self.colorize_line(body) + eol)
        return "".join(parts)

    # ---------- internal ----------

    def _render(self, t: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(t, end="")
        return cap.get()
