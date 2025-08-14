from typing import List, Protocol, Sequence

from rich.text import Text


class LineHighlighter(Protocol):
    def colorize_line(self, line: Text) -> Text:
        raise NotImplementedError("LineHighlighter.colorize_line должен быть переопределен")

    def colorize_lines(self, lines: Sequence[Text]) -> List[Text]:
        """Return a ``list`` of the *same* `Text` objects after styling in place."""
        return [self.colorize_line(t) for t in lines]
