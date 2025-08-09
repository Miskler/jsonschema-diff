from typing import Protocol


class LineHighlighter(Protocol):
    def colorize_line(self, line: str) -> str:
        raise NotImplementedError("LineHighlighter.colorize_line должен быть переопределен")
    
    def colorize_lines(self, text: str) -> str:
        out_parts: list[str] = []
        for chunk in text.splitlines(keepends=True):
            body = chunk.rstrip("\r\n")
            eol = chunk[len(body):]
            out_parts.append(self.colorize_line(body) + eol)
        return "".join(out_parts)
