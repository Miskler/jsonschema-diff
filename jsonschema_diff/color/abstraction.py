from typing import Protocol


class LineHighlighter(Protocol):
    def colorize_line(self, line: str) -> str:
        ...
    
    def colorize_lines(self, text: str) -> str:
        return "\n".join(self.colorize_line(x) for x in text.splitlines())
