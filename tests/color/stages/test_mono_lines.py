import pytest
from rich.style import Style
from rich.text import Span, Text

from jsonschema_diff.color.stages import MonoLinesHighlighter


def _first_span(line: Text) -> tuple[Span, Style]:
    """Утилита возвращает первый Span и его Style."""
    assert line.spans, "Text должен быть стилизован хотя бы один раз"
    span = line.spans[0]
    return span, span.style


# ==================================================================
#                     П Р Е Ф И К С Н Ы Е  П Р А В И Л А
# ==================================================================
@pytest.mark.parametrize(
    "raw, expected_color",
    [
        ("- removed", "red"),  # стандартные правила
        ("+ added", "green"),
        ("Rrenamed", "cyan"),  # 'r' / 'm' → cyan
    ],
)
def test_default_rules(raw, expected_color):
    hl = MonoLinesHighlighter()  # все параметры по умолчанию
    line = Text(raw)
    ret = hl.colorize_line(line)

    # тот же объект возвращён
    assert ret is line

    _, style = _first_span(line)
    assert style.color.name == expected_color
    assert style.bold is True


# ------------------------------------------------------------------
# Пользовательские правила и   **первый-совпавший**   приоритет
# ------------------------------------------------------------------
def test_custom_rules_order() -> None:
    rules = {"--": "blue", "-": "yellow"}  # порядок важен
    hl = MonoLinesHighlighter(rules=rules)

    line = Text("-- headline")
    hl.colorize_line(line)

    _, style = _first_span(line)
    assert style.color.name == "blue"  # сработал первый префикс
    assert style.bold is True


# ------------------------------------------------------------------
# Чувствительность к регистру
# ------------------------------------------------------------------
def test_case_sensitive_toggle() -> None:
    hl = MonoLinesHighlighter(case_sensitive=True, rules={"Err": "yellow"})

    ok = Text("Err failure")
    hl.colorize_line(ok)
    _, s_ok = _first_span(ok)
    assert s_ok.color.name == "yellow"

    ko = Text("err failure")  # регистр не совпадает
    hl.colorize_line(ko)
    _, s_ko = _first_span(ko)
    # правило не применилось → bold-fallback без цвета
    assert s_ko.color is None and s_ko.bold is True


# ==================================================================
#                       F A L L B A C K И
# ==================================================================
def test_default_color_fallback() -> None:
    hl = MonoLinesHighlighter(bold=False, default_color="white", rules={"*": "magenta"})
    line = Text("no-match")
    hl.colorize_line(line)

    _, style = _first_span(line)
    assert style.color.name == "white"  # сработал default_color
    assert style.bold is False


def test_bold_only_fallback() -> None:
    hl = MonoLinesHighlighter(bold=True, default_color=None, rules={})
    line = Text("plain line")
    hl.colorize_line(line)

    _, style = _first_span(line)
    assert style.color is None  # цвета нет
    assert style.bold is True  # только жирное начертание
