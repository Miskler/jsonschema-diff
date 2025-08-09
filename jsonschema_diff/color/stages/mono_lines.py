# jsonschema_diff/color/mono_rich.py
from __future__ import annotations

from typing import Mapping, Optional
from rich.console import Console
from rich.text import Text
from rich.style import Style

from ..abstraction import LineHighlighter


class MonoLinesHighlighter(LineHighlighter):
    """
    Подсветка строк по первому подходящему префиксу.
    Рендер через rich.Text -> ANSI (truecolor).
    """
    def __init__(
        self,
        bold: bool = True,
        default_color: Optional[str] = None,
        case_sensitive: bool = False,
        rules: Mapping[str, str] = {
            "-": "red",
            "+": "green",
            "r": "cyan",
            "m": "cyan",
        },
    ) -> None:
        self.bold = bold
        self.default_color = default_color
        self.case_sensitive = case_sensitive
        self.rules = dict(rules)  # сохраняем порядок
        # один Console на весь объект
        self._console = Console(force_terminal=True, color_system="truecolor", width=10_000)

    def _render(self, text: Text) -> str:
        with self._console.capture() as cap:
            self._console.print(text, end="")
        return cap.get()

    def colorize_line(self, line: str) -> str:
        probe = line if self.case_sensitive else line.lower()

        for prefix, color in self.rules.items():
            pref = prefix if self.case_sensitive else prefix.lower()
            if probe.startswith(pref):
                t = Text(line)
                t.stylize(Style(color=color, bold=self.bold), 0, len(t))
                return self._render(t)

        if self.default_color is not None:
            t = Text(line)
            t.stylize(Style(color=self.default_color, bold=self.bold), 0, len(t))
            return self._render(t)

        if self.bold:
            t = Text(line)
            t.stylize(Style(bold=True), 0, len(t))
            return self._render(t)

        return line

    def colorize_lines(self, text: str) -> str:
        out_parts: list[str] = []
        for chunk in text.splitlines(keepends=True):
            body = chunk.rstrip("\r\n")
            eol = chunk[len(body):]
            out_parts.append(self.colorize_line(body) + eol)
        return "".join(out_parts)
