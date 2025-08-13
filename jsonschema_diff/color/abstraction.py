from typing import Protocol


class LineHighlighter(Protocol):
    def colorize_line(self, line: str) -> str:
        raise NotImplementedError("LineHighlighter.colorize_line должен быть переопределен")
    
    def colorize_lines(self, text: str | list[str]) -> str:
        out_parts: list[str] = []
        split_lines = text if isinstance(text, list) else text.splitlines(keepends=True)
        for chunk in split_lines:
            body = chunk.rstrip("\r\n")
            eol = chunk[len(body):]
            out_parts.append(self.colorize_line(body) + eol)
        return "".join(out_parts)
