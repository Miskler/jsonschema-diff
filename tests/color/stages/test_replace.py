"""
Проверяем:

* ранний выход, если нет ':' или нет '->';
* подсветку отличий старыx / новых токенов фоном;
* опциональную перекраску стрелки;
* работу параметра underline_changes;
* «batch»-обработку методом .colorize_lines().
"""

from __future__ import annotations

from typing import List

from rich.text import Text


# ------------------------------------------------------------------
# Робкий импорт — модуль может лежать либо «плоско», либо в пакете
# ------------------------------------------------------------------
from jsonschema_diff.color.stages import ReplaceGenericHighlighter


# ------------------------------------------------------------------
# Утилиты для проверки стилей
# ------------------------------------------------------------------
def style_at(text: Text, idx: int):
    """Возвращает Style применённый к символу с индексом *idx*."""
    style = None
    for span in text.spans:
        if span.start <= idx < span.end:
            style = span.style          # «побеждает» последний
    return style


# ==================================================================
#                           Т Е С Т Ы
# ==================================================================
def test_line_without_colon_is_untouched():
    hl = ReplaceGenericHighlighter()
    txt = Text("no colon here -> still nothing")
    hl.colorize_line(txt)
    assert txt.spans == []


def test_line_without_arrow_is_untouched():
    hl = ReplaceGenericHighlighter()
    txt = Text(".path: only old value")
    hl.colorize_line(txt)
    assert txt.spans == []


def test_diff_highlighting_and_arrow_color():
    hl = ReplaceGenericHighlighter(arrow_color="yellow")

    raw = ".field: red -> blue"
    txt = Text(raw)
    hl.colorize_line(txt)

    # индексы первого символа изменённых слов
    idx_old = raw.index("r")          # 'r' в «red»
    idx_new = raw.index("b")          # 'b' в «blue»
    idx_arrow = raw.index("-")        # «–>»

    old_style = style_at(txt, idx_old)
    new_style = style_at(txt, idx_new)
    arrow_style = style_at(txt, idx_arrow)

    assert old_style.bgcolor.name == "grey35"
    assert new_style.bgcolor.name == "grey35"
    assert arrow_style.color.name == "yellow"
    # фон у стрелки не должен быть закрашен
    assert arrow_style.bgcolor is None


def test_underline_changes_flag():
    hl = ReplaceGenericHighlighter(underline_changes=True)
    txt = Text(".p: one -> two")
    hl.colorize_line(txt)

    assert style_at(txt, txt.plain.index("o")).underline is True   # «one»
    assert style_at(txt, txt.plain.index("t")).underline is True   # «two»


def test_colorize_lines_batch_returns_same_objects():
    lines: List[Text] = [Text(f".x{i}: {i} -> {i+1}") for i in range(3)]
    hl = ReplaceGenericHighlighter()
    out = hl.colorize_lines(lines)

    # возвращён тот же список объектов
    assert out == lines
    # у каждого текста есть хотя бы один Span после обработки
    assert all(t.spans for t in lines)
