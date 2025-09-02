from __future__ import annotations

"""
Composable *Rich*-native colouring pipeline
==========================================

Provides :class:`HighlighterPipeline`, an orchestrator that feeds raw
multi-line strings through a chain of :class:`LineHighlighter` stages.
Each stage operates on :class:`rich.text.Text` so it can add style spans
without mutating the text itself.

Typical usage
-------------

>>> pipeline = HighlighterPipeline([MySyntaxHL(), MyDiffHL()])
>>> ansi_output = pipeline.colorize_and_render(src_string)
print(ansi_output)
"""

from typing import TYPE_CHECKING, Iterable

from rich.console import Console
from rich.text import Text

if TYPE_CHECKING:  # pragma: no cover
    from .abstraction import LineHighlighter


class HighlighterPipeline:  # noqa: D101
    """Chain of :pyclass:`LineHighlighter` stages.

    Parameters
    ----------
    stages :
        Iterable of :class:`LineHighlighter` instances.  The iterable is
        immediately materialised into a list so the pipeline can be reused.

    Note
    ----
    * Each input line is passed through **every** stage in order.
    * If a stage exposes a bulk :pyfunc:`colorize_lines` method it is
      preferred over per-line iteration for performance.
    """

    def __init__(self, stages: Iterable["LineHighlighter"]):
        self.stages: list["LineHighlighter"] = list(stages)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def colorize(self, text: str) -> Text:
        """Return a rich ``Text`` object with all styles applied.

        Parameters
        ----------
        text :
            Multi-line string to be colourised.

        Returns
        -------
            One composite `Text` built by joining all styled lines with
            ``\\n`` separators.
        """
        lines = text.splitlines()
        rich_lines = [Text(line) for line in lines]

        for stage in self.stages:
            colorize_lines = getattr(stage, "colorize_lines", None)
            if callable(colorize_lines):
                colorize_lines(rich_lines)
            else:
                for rl in rich_lines:
                    stage.colorize_line(rl)
        return Text("\n").join(rich_lines)

    def colorize_and_render(
        self,
        text: str,
        auto_line_wrapping: bool = False,
    ) -> str:
        """Colourise and immediately render to ANSI.

        Parameters
        ----------
        text :
            Multi-line input string.

        Returns
        -------
            ANSI-encoded string ready for terminal output.
        """
        rich_lines = self.colorize(text)

        console = Console(
            force_terminal=True,
            color_system="truecolor",
            width=self._detect_width() if auto_line_wrapping else None,
            legacy_windows=False,
        )
        with console.capture() as cap:
            console.print(rich_lines, end="")
        return cap.get()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _detect_width(default: int = 2048) -> int:  # noqa: D401
        """Best-effort terminal width detection.

        Falls back to *default* when a real TTY is not present
        (e.g. in CI).

        Parameters
        ----------
        default :
            Width to use when detection fails.  Defaults to ``512``.

        Returns
        -------
            Column count deemed safe for rendering.
        """
        try:
            from shutil import get_terminal_size

            return max(get_terminal_size().columns, 20)
        except Exception:  # pragma: no cover
            return default
