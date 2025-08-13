from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .abstraction import LineHighlighter


class HighlighterPipeline:
    def __init__(self, stages: Iterable["LineHighlighter"]):
        self.stages = list(stages)

    def colorize_line(self, line: str) -> str:
        out = line
        for h in self.stages:
            out = h.colorize_line(out)
        return out

    def colorize_lines(self, text: str | list[str]) -> str:
        out = text
        for h in self.stages:
            out = h.colorize_lines(out)
        return out
