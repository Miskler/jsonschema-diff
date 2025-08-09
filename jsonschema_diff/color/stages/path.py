# jsonschema_diff/color/path_stage_rich.py
from __future__ import annotations

from typing import Optional, List, Tuple
from rich.console import Console
from rich.text import Text
from rich.style import Style

from ..abstraction import LineHighlighter


class PathHighlighter(LineHighlighter):
    """
    Подсветка компонент пути (учитывает ':' для определения финального проперти):
      .$defs["item"]["blocks"][0]["type"].rangeLength
      ["tags"][0].rangeLength
      .range

    Цвета:
      - base_color:     '.', '[', ']'
      - string_color:   "..." / '...' (включая кавычки, внутри скобок)
      - number_color:   числа (внутри скобок)
      - path_prop_color:промежуточные свойства (.foo .bar)
      - prop_color:     финальное свойство (.rangeLength) — имя прямо перед ':' (игнорируя пробелы)
                        точка остаётся base_color
    """

    def __init__(
        self,
        *,
        base_color: str = "grey70",
        string_color: str = "yellow",
        number_color: str = "magenta",
        path_prop_color: str = "color(103)",
        prop_color: str = "color(146)",
    ) -> None:
        self.base_style = Style(color=base_color)
        self.string_style = Style(color=string_color)
        self.number_style = Style(color=number_color)
        self.path_prop_style = Style(color=path_prop_color)
        self.prop_style = Style(color=prop_color)
        self._console = Console(force_terminal=True, color_system="truecolor", width=10_000)

    def colorize_line(self, line: str) -> str:
        text = Text.from_ansi(line)
        s = text.plain

        # границы пути
        first_dot = s.find(".")
        first_br  = s.find("[")
        starts = [i for i in (first_dot, first_br) if i != -1]
        if not starts:
            return line
        path_start = min(starts)
        colon = s.find(":")
        path_end = colon if colon != -1 else len(s)
        if path_start >= path_end:
            return line

        # посимвольный скан: собираем имена после точки
        i = path_start
        dot_name_spans: List[Tuple[int, int]] = []  # абсолютные [start,end) для имён после '.'

        def is_ident_start(ch: str) -> bool:
            return ch.isalpha() or ch in "_$"
        def is_ident_part(ch: str) -> bool:
            return ch.isalnum() or ch in "_$"

        while i < path_end:
            ch = s[i]

            # .identifier
            if ch == "." and i + 1 < path_end and is_ident_start(s[i + 1]):
                # точка — базовым
                text.stylize(self.base_style, i, i + 1)
                j = i + 2
                while j < path_end and is_ident_part(s[j]):
                    j += 1
                dot_name_spans.append((i + 1, j))  # имя без точки
                i = j
                continue

            # [ ... ]
            if ch == "[":
                # '['
                text.stylize(self.base_style, i, i + 1)
                j = i + 1
                while j < path_end and s[j] != "]":
                    j += 1
                inner_start = i + 1
                inner_end = j
                if inner_start < inner_end:
                    inner = s[inner_start:inner_end]
                    inner_stripped = inner.strip()
                    # "..." / '...'
                    if (inner_stripped.startswith('"') and inner_stripped.endswith('"')) or \
                       (inner_stripped.startswith("'") and inner_stripped.endswith("'")):
                        lead_ws = len(inner) - len(inner.lstrip())
                        trail_ws = len(inner) - len(inner.rstrip())
                        a = inner_start + lead_ws
                        b = inner_end - trail_ws
                        text.stylize(self.string_style, a, b)
                    else:
                        # числа
                        k = inner_start
                        while k < inner_end:
                            if s[k].isspace():
                                k += 1
                                continue
                            if s[k] == "-" or s[k].isdigit():
                                t0 = k
                                if s[k] == "-":
                                    k += 1
                                while k < inner_end and s[k].isdigit():
                                    k += 1
                                text.stylize(self.number_style, t0, k)
                            else:
                                k += 1
                # ']'
                if j < path_end and s[j] == "]":
                    text.stylize(self.base_style, j, j + 1)
                    i = j + 1
                else:
                    i = path_end
                continue

            i += 1

        # --- выбор финального свойства с участием ':' ---
        final_idx: Optional[int] = None
        if dot_name_spans:
            # позиция последнего непробельного символа перед ':' (или path_end)
            k = path_end - 1
            while k >= path_start and s[k].isspace():
                k -= 1
            # если этот символ попадает внутрь имени после точки — это финальный проп
            for idx, (a, b) in enumerate(dot_name_spans):
                if a <= k < b:
                    final_idx = idx
            # резерв: если перед ':' не имя, а ']' и т.п. — берём последнюю точку до ':'
            if final_idx is None:
                final_idx = len(dot_name_spans) - 1

            # покрасить имена
            for idx, (a, b) in enumerate(dot_name_spans):
                style = self.prop_style if idx == final_idx else self.path_prop_style
                text.stylize(style, a, b)

        # дополнительно — окрасить любые точки и скобки базовым (на случай, если не поймали выше)
        seg = s[path_start:path_end]
        for off, ch in enumerate(seg):
            if ch == "." or ch == "[" or ch == "]":
                pos = path_start + off
                text.stylize(self.base_style, pos, pos + 1)

        # подсветить двоеточие базовым цветом
        if colon != -1:
            text.stylize(self.base_style, colon, colon + 1)

        return self._render(text)

    def colorize_lines(self, text_block: str) -> str:
        out: list[str] = []
        for chunk in text_block.splitlines(keepends=True):
            line = chunk.rstrip("\r\n")
            eol = chunk[len(line):]
            out.append(self.colorize_line(line) + eol)
        return "".join(out)

    def _render(self, t: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(t, end="")
        return cap.get()
