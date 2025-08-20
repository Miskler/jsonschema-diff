from __future__ import annotations

"""
Monochrome prefix-based high-lighter
====================================

A :class:`~jsonschema_diff.color.abstraction.LineHighlighter` that decorates a
single :class:`rich.text.Text` *in-place* by looking at its **first matching
prefix**—typically the leading character produced by *unified diff* output
(``-``, ``+``, *etc.*).

Why a “Rich-native” rewrite?
----------------------------
The original *jsonschema-diff* implementation rendered to a string containing
ANSI escape codes.  In interactive TUI applications you often want to keep the
object as a real ``Text`` so you can:

* put it into a :class:`rich.table.Table`,
* display it inside a :class:`rich.panel.Panel`,
* or update it live without re-parsing ANSI.

This drop-in replacement keeps behaviour identical while removing the ANSI
round-trip.
"""
from typing import Mapping, Optional

from rich.style import Style
from rich.text import Text

from ..abstraction import LineHighlighter


class MonoLinesHighlighter(LineHighlighter):
    """Colourise one line based on a prefix lookup.

    Parameters
    ----------
    bold :
        Apply the *bold* attribute together with the foreground colour.
        Enabled by default to keep parity with the original.
    default_color :
        Fallback colour when no rule matches.  If *None* the line is left
        unchanged (except for *bold* when that option is *True*).
    case_sensitive :
        Whether prefix matching should be case-sensitive.  Defaults to *False*.
    rules :
        Mapping ``prefix → colour``.  The first match wins; order is therefore
        significant.  If *None*, the following defaults are used::

            {
                "-": "red",
                "+": "green",
                "r": "cyan",
                "m": "cyan",
            }
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
        self.rules: Mapping[str, str] = dict(rules)  # preserve order

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def colorize_line(self, line: Text) -> Text:
        """Apply a single style pass **in place**.

        Parameters
        ----------
        line :
            The :class:`rich.text.Text` instance to be modified.

        Returns
        -------
        rich.text.Text
            **The very same instance** that was passed in—allowing fluent,
            chainable APIs.

        Note
        ----
        Only the *first* matching prefix is honoured; subsequent rules are
        ignored, mirroring classic *grep* / *sed* behaviour.
        """
        probe = line.plain if self.case_sensitive else line.plain.lower()

        for prefix, color in self.rules.items():
            pref = prefix if self.case_sensitive else prefix.lower()
            if probe.startswith(pref):
                line.stylize(Style(color=color, bold=self.bold), 0, len(line))
                return line  # first match wins

        # --- fall-back -------------------------------------------------
        if self.default_color is not None:
            line.stylize(Style(color=self.default_color, bold=self.bold), 0, len(line))
        elif self.bold:
            line.stylize(Style(bold=True), 0, len(line))
        return line
