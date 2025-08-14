"""
Тесты проверяют:

* игнор строк без пути;
* окраску:
    • точечных идентификаторов (path-prop / prop);
    • строковых литералов в скобках;
    • числовых индексов в скобках;
    • служебных символов «.  [ ] :» базовым стилем.
"""

from __future__ import annotations

import importlib
import importlib.util
import pathlib
import sys
import types

import pytest
from rich.text import Text


# ---------------------------------------------------------------------------
# Надёжный импорт даже в «плоской» распаковке исходников
# ---------------------------------------------------------------------------
def _import_path_highlighter():
    """
    • Сначала пытаемся импортировать штатный модуль
      «jsonschema_diff.color.stages.path».
    • Если пакетов нет (файлы просто лежат в корне), создаём их «на лету»
      и загружаем path.py вручную.
    """
    try:
        return importlib.import_module("jsonschema_diff.color.stages.path").PathHighlighter
    except ModuleNotFoundError:
        # ── создаём пустые namespace-пакеты ──────────────────────────────
        for pkg in ("jsonschema_diff", "jsonschema_diff.color", "jsonschema_diff.color.stages"):
            if pkg not in sys.modules:
                pkg_mod = types.ModuleType(pkg)
                pkg_mod.__path__ = []           # помечаем как package
                sys.modules[pkg] = pkg_mod
            elif not hasattr(sys.modules[pkg], "__path__"):
                sys.modules[pkg].__path__ = []

        # ── подгружаем abstraction.py, т.к. path.py делает «..abstraction»
        root_dir = pathlib.Path(__file__).resolve().parents[4]  # <repo-root>
        abst_path = root_dir / "abstraction.py"
        if "jsonschema_diff.color.abstraction" not in sys.modules and abst_path.exists():
            spec = importlib.util.spec_from_file_location(
                "jsonschema_diff.color.abstraction", abst_path
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules["jsonschema_diff.color.abstraction"] = mod
            spec.loader.exec_module(mod)        # type: ignore[arg-type]

        # ── подгружаем сам path.py под «правильным» именем ───────────────
        path_path = root_dir / "path.py"
        spec = importlib.util.spec_from_file_location(
            "jsonschema_diff.color.stages.path", path_path
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["jsonschema_diff.color.stages.path"] = mod
        spec.loader.exec_module(mod)            # type: ignore[arg-type]
        return mod.PathHighlighter


PathHighlighter = _import_path_highlighter()

# ---------------------------------------------------------------------------
# Вспомогалки для проверки цвета символа
# ---------------------------------------------------------------------------
def color_at(text: Text, idx: int) -> str | None:
    """Возвращает *имя* цвета, применённого к символу с данным индексом."""
    style = None
    for span in text.spans:
        if span.start <= idx < span.end:
            style = span.style            # «побеждает» последний
    return style.color.name if style and style.color else None


HL = PathHighlighter(
    base_color="white",
    string_color="red",
    number_color="blue",
    path_prop_color="green",
    prop_color="yellow",
)

# ---------------------------------------------------------------------------
#                                Т Е С Т Ы
# ---------------------------------------------------------------------------
def test_line_without_path_is_untouched():
    text = Text("plain message")
    HL.colorize_line(text)
    assert text.spans == []


def test_dot_path_highlighting():
    raw = ".parent.child: value"
    txt = Text(raw)
    HL.colorize_line(txt)

    # точки и ':' – базовый белый
    assert color_at(txt, 0) == "white"
    assert color_at(txt, raw.index(".", 1)) == "white"
    assert color_at(txt, raw.index(":")) == "white"

    # первый идентификатор («parent») – зелёный
    assert color_at(txt, 1) == "green"
    # последний («child») – жёлтый
    assert color_at(txt, raw.index("c")) == "yellow"


def test_bracketed_strings_highlighting():
    raw = '["user"]["name"]:'
    txt = Text(raw)
    HL.colorize_line(txt)

    # кавычные строки — красные
    assert color_at(txt, 2) == "red"      # «u» из "user"
    assert color_at(txt, 10) == "red"     # «n» из "name"

    # скобки и ':' — белые
    for i, ch in enumerate(raw):
        if ch in "[]:":
            assert color_at(txt, i) == "white"


def test_numeric_indexes_highlighting():
    raw = "[0][-12]"
    txt = Text(raw)
    HL.colorize_line(txt)

    # числа — синие
    assert color_at(txt, 1) == "blue"     # 0
    assert color_at(txt, 4) == "blue"     # 1
    assert color_at(txt, 5) == "blue"     # 2

    # скобки — белые
    for i, ch in enumerate(raw):
        if ch in "[]":
            assert color_at(txt, i) == "white"
