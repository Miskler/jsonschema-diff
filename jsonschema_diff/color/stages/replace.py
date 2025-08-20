from __future__ import annotations

"""
Token-level diff high-lighter
=============================

A Rich-native replacement for the original ``ReplaceGenericHighlighter`` that
marks *token-by-token* differences inside a ``OLD -> NEW`` tail.  It operates
directly on :class:`rich.text.Text` so you can embed the result in Rich tables
or live dashboards without ANSI parsing.

Detection strategy
------------------
#) Split *OLD* and *NEW* into tokens (numbers, words, spaces, punctuation).
#) Run :class:`difflib.SequenceMatcher` to classify *replace*, *delete*,
   *insert* spans.
#) Apply background colour ± underline only to the differing tokens.

Everything left of the first ``:`` is treated as an opaque *head*.
"""
import difflib
import re
from typing import List, Optional, Tuple

from rich.style import Style
from rich.text import Text

from ..abstraction import LineHighlighter


class ReplaceGenericHighlighter(LineHighlighter):
    """Highlight token differences in ``OLD -> NEW`` tails.

    Parameters
    ----------
    bg_color :
        Background colour used to mark differing spans.
    arrow_color :
        Optional foreground colour for the ``->`` arrow.
    case_sensitive :
        Compare tokens case-sensitively when *True* (default).
    underline_changes :
        Underline differing spans in addition to background colour.
    """

    # -- regex patterns & helpers -------------------------------------
    _TAIL_PATTERN = re.compile(
        r"(?P<left_ws>\s*)"  # leading spaces
        r"(?P<old>.*?)"  # OLD
        r"(?P<between_ws>\s*)"
        r"(?P<arrow>->)"
        r"(?P<right_ws>\s*)"
        r"(?P<new>.*?)"  # NEW
        r"(?P<trailing_ws>\s*)$",
    )

    _TOKEN_RE = re.compile(
        r"""
        (?P<num>[+-]?\d+(?:[.,]\d+)?(?:[a-z%]+)?|∞) |
        (?P<word>\w+)                                |
        (?P<space>\s+)                               |
        (?P<punc>.?)
        """,
        re.VERBOSE | re.UNICODE,
    )

    # -----------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------
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

        self._bg_style = Style(bgcolor=self.bg_color, underline=self.underline_changes)
        self._arrow_style = Style(color=self.arrow_color) if self.arrow_color else None

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def colorize_line(self, line: Text) -> Text:
        """Apply diff-based styling **in place**.

        Parameters
        ----------
        line :
            The :class:`rich.text.Text` instance containing a diff line.

        Returns
        -------
        rich.text.Text
            The same object, now decorated with background and/or underline
            spans on the differing tokens.
        """
        plain = line.plain

        # 1) locate first ':' — tail is everything to its right
        colon_idx = plain.find(":")
        if colon_idx == -1:
            return line

        head_plain = plain[: colon_idx + 1]
        tail_plain = plain[colon_idx + 1 :]

        m = self._TAIL_PATTERN.match(tail_plain)
        if not m:
            return line  # format didn't match

        # 2) extract tail pieces
        left_ws = m.group("left_ws")
        old_text = m.group("old")
        between_ws = m.group("between_ws")
        arrow = m.group("arrow")
        right_ws = m.group("right_ws")
        new_text = m.group("new")

        # 3) absolute indices within *plain* string
        base = len(head_plain)
        old_start = base + len(left_ws)
        old_end = old_start + len(old_text)

        arrow_start = old_end + len(between_ws)
        arrow_end = arrow_start + len(arrow)

        new_start = arrow_end + len(right_ws)

        # 4) diff tokens
        old_tokens = self._tokenize(old_text)
        new_tokens = self._tokenize(new_text)

        sm = difflib.SequenceMatcher(
            a=[t[3] for t in old_tokens],
            b=[t[3] for t in new_tokens],
        )

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            # OLD side: replace/delete
            if tag in ("replace", "delete"):
                span = self._span_from_tokens(old_tokens, i1, i2)
                if span:
                    s, e = span
                    line.stylize(self._bg_style, old_start + s, old_start + e)
            # NEW side: replace/insert
            if tag in ("replace", "insert"):
                span = self._span_from_tokens(new_tokens, j1, j2)
                if span:
                    s, e = span
                    line.stylize(self._bg_style, new_start + s, new_start + e)

        # 5) recolour arrow if requested
        if self._arrow_style:
            line.stylize(self._arrow_style, arrow_start, arrow_end)

        return line

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _tokenize(self, s: str) -> List[Tuple[str, int, int, str]]:
        """Return token list: ``(raw, start, end, cmp)``."""
        toks: List[Tuple[str, int, int, str]] = []
        for m in self._TOKEN_RE.finditer(s):
            raw = m.group(0)
            cmpv = raw if self.case_sensitive else raw.lower()
            toks.append((raw, m.start(), m.end(), cmpv))
        return toks

    @staticmethod
    def _span_from_tokens(
        tokens: List[Tuple[str, int, int, str]],
        i1: int,
        i2: int,
    ) -> Optional[Tuple[int, int]]:
        if i1 >= i2:
            return None
        return tokens[i1][1], tokens[i2 - 1][2]
