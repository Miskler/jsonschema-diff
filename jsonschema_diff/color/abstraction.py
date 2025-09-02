"""
Abstraction for line-based high-lighters
=======================================

This module defines :class:`LineHighlighter`, a thin
:class:`typing.Protocol` that specifies the minimal contract required by the
colour pipeline implemented in :pyfile:`base.py`.

Implementors are expected to decorate :class:`rich.text.Text` objects **in
place**; therefore methods must not alter the underlying string content –
only styling metadata.
"""

from typing import List, Protocol, Sequence

from rich.text import Text


class LineHighlighter(Protocol):
    """Protocol for single-line high-lighters.

    Concrete implementations *may* also override
    :meth:`colorize_lines` for bulk operations, but
    :meth:`colorize_line` is the only mandatory method.
    """

    def colorize_line(self, line: Text) -> Text:
        """Stylise one line **in-place** and return it.

        Parameters
        ----------
        line :
            A single :class:`rich.text.Text` instance to be colour-styled.

        Returns
        -------
            The **same** `Text` object, now containing style spans.

        Raises
        ------
        NotImplementedError
            Always here; concrete subclasses must override this method.
        """
        raise NotImplementedError("LineHighlighter.colorize_line должен быть переопределен")

    def colorize_lines(self, lines: Sequence[Text]) -> List[Text]:
        """Vectorised helper that stylises a *sequence* of lines.

        The naïve fallback simply delegates to :meth:`colorize_line`.

        Parameters
        ----------
        lines :
            Ordered collection of :class:`rich.text.Text` objects.

        Returns
        -------
            The original objects, now styled in place.
        """
        return [self.colorize_line(t) for t in lines]
