from __future__ import annotations

"""
A variant of ``MonoLinesHighlighter`` that **accepts a `rich.text.Text` object**
and returns **the very same instance** after applying the style rules in place.

The original implementation converted the line to a string and rendered ANSI
codes through a ``Console`` capture.  In many scenarios—e.g. when building a
Rich table, panel, or live‑update widget—you often need to keep working with
`Text` objects instead of rendered strings.  This rewrite is a drop‑in
replacement for that use‑case.
"""

from typing import Mapping, Optional

from rich.text import Text
from rich.style import Style

from ..abstraction import LineHighlighter


class MonoLinesHighlighter(LineHighlighter):
    """Highlight a line **in place** based on the first matching prefix.

    Parameters
    ----------
    bold:
        Whether to apply the *bold* attribute when a style is applied.  Defaults
        to *True* to keep visual parity with the original version.
    default_color:
        Fallback colour to use when no rule matches.  If *None*, the line is
        left unchanged unless ``bold`` is *True*.
    case_sensitive:
        Whether prefix matching should be case‑sensitive.  Defaults to
        *False* (original behaviour).
    rules:
        Mapping *prefix → colour*.  The mapping order is preserved so the first
        match wins, exactly as before.
    """

    def __init__(
        self,
        bold: bool = True,
        default_color: Optional[str] = None,
        case_sensitive: bool = False,
        rules: Mapping[str, str] | None = None,
    ) -> None:
        if rules is None:
            rules = {
                "-": "red",
                "+": "green",
                "r": "cyan",
                "m": "cyan",
            }
        self.bold = bold
        self.default_color = default_color
        self.case_sensitive = case_sensitive
        # preserve order of the user‑supplied mapping
        self.rules: Mapping[str, str] = dict(rules)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def colorize_line(self, line: Text) -> Text:  # noqa: D401  (imperative mood)
        """Apply style **in place** and return *the same* ``Text`` instance."""
        probe = line.plain if self.case_sensitive else line.plain.lower()

        for prefix, color in self.rules.items():
            pref = prefix if self.case_sensitive else prefix.lower()
            if probe.startswith(pref):
                line.stylize(Style(color=color, bold=self.bold), 0, len(line))
                return line  # we are done: first match wins

        # --- No rule matched: fallbacks ----------------------------------
        if self.default_color is not None:
            line.stylize(Style(color=self.default_color, bold=self.bold), 0, len(line))
        elif self.bold:
            # Apply only bold; keeps parity with original behaviour
            line.stylize(Style(bold=True), 0, len(line))
        return line
