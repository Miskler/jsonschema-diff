from __future__ import annotations

"""Composable *Rich*-native high‑lighting pipeline.

The original utilities coloured lines via ANSI strings; after rewriting the
individual high‑lighters to operate on :class:`rich.text.Text`, we still need a
simple orchestrator that turns **raw strings → Text → styled Text** and—when
required—renders them back to ANSI for CLI output.
"""

from typing import Iterable, List, Sequence, TYPE_CHECKING
from rich.text import Text
from rich.console import Console

if TYPE_CHECKING:  # pragma: no cover
    from .abstraction import LineHighlighter  # noqa: F401  (imported for typing only)


class HighlighterPipeline:  # noqa: D101 (docstring just above)
    def __init__(self, stages: Iterable["LineHighlighter"]):
        # materialise into a list so we can iterate multiple times
        self.stages: list["LineHighlighter"] = list(stages)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def colorize(self, text: str) -> Text:  # noqa: D401
        """Return a list of *new* ``Text`` objects after applying all stages."""
        lines = text.splitlines()
        rich_lines = [Text(l) for l in lines]

        for stage in self.stages:
            # prefer the vectorised helper when available — it's faster
            colorize_lines = getattr(stage, "colorize_lines", None)
            if callable(colorize_lines):
                colorize_lines(rich_lines)  # type: ignore[arg-type]
            else:
                for rl in rich_lines:
                    stage.colorize_line(rl)
        return Text("\n").join(rich_lines)

    def colorize_and_render(self, text: str) -> str:
        """Colourise and *immediately* render each line to an ANSI string."""
        rich_lines = self.colorize(text)

        # Use a throw‑away Console so we don't affect the caller's Console config
        console = Console(
            force_terminal=True,  # ensure ANSI codes even when not attached to tty
            color_system="truecolor",
            width=self._detect_width(),  # avoid unwanted wrapping
            legacy_windows=False,
        )

        with console.capture() as cap:
            console.print(rich_lines, end="")  # prevent extra newline
        return cap.get()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _detect_width(default: int = 512) -> int:  # noqa: D401
        """Detect terminal width or fall back to *default*.

        Using a very wide width avoids Rich's soft‑wrapping which would mutate
        line contents during capture.
        """
        try:
            from shutil import get_terminal_size

            return max(get_terminal_size().columns, 20)
        except Exception:  # pragma: no cover — environment might be stubbed/missing
            return default

        