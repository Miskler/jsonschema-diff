from __future__ import annotations

"""
JSON-Pointer path high-lighter
==============================

Rich-native version of the original ``PathHighlighter`` that styles a
:class:`rich.text.Text` object **in place** instead of emitting raw ANSI.  It
distinguishes:

* brackets ``[ ... ]`` and dots ``.``  → *base colour*
* quoted strings inside brackets      → *string colour*
* numbers inside brackets             → *number colour*
* property names before the final ``:``:
  * intermediate path components      → *path_prop colour*
  * the final property                → *prop colour*

Only the public constructor and :meth:`colorize_line` are part of the public
API; everything else is an implementation detail.
"""
from typing import List, Optional, Tuple

from rich.style import Style
from rich.text import Text

from ..abstraction import LineHighlighter


class PathHighlighter(LineHighlighter):
    """Colourise JSON-pointer-like paths.

    Parameters
    ----------
    base_color :
        Colour for structural characters (``.[]:``).
    string_color :
        Colour for quoted strings inside brackets.
    number_color :
        Colour for numeric indices inside brackets.
    path_prop_color :
        Colour for non-final property names.
    prop_color :
        Colour for the final property (right before the ``:``).
    """

    def __init__(  # noqa: D401 – imperative mood is fine in NumPy style
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def colorize_line(self, line: Text) -> Text:
        """Apply path styling **in place** and return the same ``Text``.

        Parameters
        ----------
        line :
            The :class:`rich.text.Text` object to be stylised.

        Returns
        -------
        rich.text.Text
            The *modified* object (for fluent method chaining).
        """
        s = line.plain

        # --- Find path boundaries -------------------------------------
        first_dot = s.find(".")
        first_br = s.find("[")
        starts = [i for i in (first_dot, first_br) if i != -1]
        if not starts:
            return line  # nothing to colourise
        path_start = min(starts)
        colon = s.find(":")
        path_end = colon if colon != -1 else len(s)
        if path_start >= path_end:
            return line

        # --- Scan char‑by‑char to locate identifiers and brackets ------
        i = path_start
        dot_name_spans: List[Tuple[int, int]] = []  # absolute [start,end)

        def is_ident_start(ch: str) -> bool:
            return ch.isalpha() or ch in "_$"

        def is_ident_part(ch: str) -> bool:
            return ch.isalnum() or ch in "_$"

        while i < path_end:
            ch = s[i]

            # .identifier
            if ch == "." and i + 1 < path_end and is_ident_start(s[i + 1]):
                # the dot itself
                line.stylize(self.base_style, i, i + 1)
                j = i + 2
                while j < path_end and is_ident_part(s[j]):
                    j += 1
                dot_name_spans.append((i + 1, j))  # name without the dot
                i = j
                continue

            # [ ... ]
            if ch == "[":
                # '['
                line.stylize(self.base_style, i, i + 1)
                j = i + 1
                while j < path_end and s[j] != "]":
                    j += 1

                inner_start = i + 1
                inner_end = j
                if inner_start < inner_end:
                    inner = s[inner_start:inner_end]
                    inner_stripped = inner.strip()
                    # quoted string  "..." / '...'
                    if (inner_stripped.startswith('"') and inner_stripped.endswith('"')) or (
                        inner_stripped.startswith("'") and inner_stripped.endswith("'")
                    ):
                        lead_ws = len(inner) - len(inner.lstrip())
                        trail_ws = len(inner) - len(inner.rstrip())
                        a = inner_start + lead_ws
                        b = inner_end - trail_ws
                        line.stylize(self.string_style, a, b)
                    else:
                        # numbers
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
                                line.stylize(self.number_style, t0, k)
                            else:
                                k += 1
                # ']'
                if j < path_end and s[j] == "]":
                    line.stylize(self.base_style, j, j + 1)
                    i = j + 1
                else:
                    i = path_end
                continue

            i += 1

        # --- Determine final property (before ':') ---------------------
        final_idx: Optional[int] = None
        if dot_name_spans:
            k = path_end - 1
            while k >= path_start and s[k].isspace():
                k -= 1
            for idx, (a, b) in enumerate(dot_name_spans):
                if a <= k < b:
                    final_idx = idx
            if final_idx is None:
                final_idx = len(dot_name_spans) - 1

            # colourise property names
            for idx, (a, b) in enumerate(dot_name_spans):
                style = self.prop_style if idx == final_idx else self.path_prop_style
                line.stylize(style, a, b)

        # --- Ensure dots & brackets use base style ---------------------
        seg = s[path_start:path_end]
        for off, ch in enumerate(seg):
            if ch in ".[]":
                pos = path_start + off
                line.stylize(self.base_style, pos, pos + 1)

        # highlight ':' with base style
        if colon != -1:
            line.stylize(self.base_style, colon, colon + 1)

        return line
