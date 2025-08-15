from types import SimpleNamespace

import pytest
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

# ------------------------------------------------------------
# Надёжный импорт: «плоский» файл или пакет jsonschema_diff
# ------------------------------------------------------------
from jsonschema_diff.table_render import (
    Cell,
    ColumnConfig,
    LegendRenderer,
    _is_rich_renderable,
    make_standard_renderer,
)


# =================================================================
#                    Ф У Н К Ц И О Н А Л Ь Н Ы Е  Т Е С Т Ы
# =================================================================
# ---------- helpers ------------------------------------------------
class DummyRenderable(Text):
    """Rich-совместимый объект для _is_rich_renderable()."""


# ---------- _is_rich_renderable -----------------------------------
def test_is_rich_renderable_detects_rich_objects():
    assert _is_rich_renderable(Text("hi")) is True
    assert _is_rich_renderable(DummyRenderable("ok")) is True
    assert _is_rich_renderable(123) is False
    assert _is_rich_renderable("str") is False


# ---------- ColumnConfig.header_text ------------------------------
def test_column_header_text():
    cc1 = ColumnConfig("name")
    cc2 = ColumnConfig("name", header="NAME")
    assert cc1.header_text() == "name"
    assert cc2.header_text() == "NAME"


# ---------- Cell.renderable() -------------------------------------
def test_cell_renderable_padding_variants():
    c1 = Cell("val", pad=True)
    assert isinstance(c1.renderable(), Padding)

    txt = Text("rich")
    c2 = Cell(txt, pad=False)
    assert c2.renderable() is txt


# ---------- LegendRenderer._apply_processor -----------------------
def test_apply_processor_variants():
    lr = LegendRenderer([ColumnConfig("x")])

    # без processor
    assert lr._apply_processor("v", None) == "v"

    # dict → kwargs
    def proc(a, b):
        return a + b

    assert lr._apply_processor({"a": 1, "b": 2}, proc) == 3

    # list из dict/tuple/скаляров
    def proc2(x=0, **kw):
        return kw.get("x", x) + 1

    val = [{"x": 1}, (2,), 3]
    assert lr._apply_processor(val, proc2) == [2, 3, 4]


# ---------- LegendRenderer._make_cell -----------------------------
def test_make_cell_all_branches():
    lr = LegendRenderer([ColumnConfig("x")])

    # rich renderable
    cell_rich = lr._make_cell(Text("hi"), pad=True)
    assert cell_rich.pad is True

    # str / None
    cell_str = lr._make_cell("abc", pad=False)
    assert cell_str.value == "abc"

    # list mix
    mixed = ["foo", Text("bar")]
    cell_list = lr._make_cell(mixed, pad=True)
    assert cell_list.pad is False and isinstance(cell_list.value, Table)

    # fallback repr
    obj = SimpleNamespace(a=1)
    cell_obj = lr._make_cell(obj, pad=True)
    assert cell_obj.value == repr(obj)


# ---------- _validate_legends & render ----------------------------
class GoodLegend:
    @staticmethod
    def legend():
        return {"element": "*", "description": "good", "example": "ok"}


class BadLegend:
    @staticmethod
    def legend():
        return {"element": "*", "description": "miss"}  # нет example


def test_validate_legends_raises_on_missing_keys():
    lr = make_standard_renderer()
    with pytest.raises(KeyError):
        lr.render([BadLegend])


def test_render_produces_table_and_applies_example_processor():
    lr = make_standard_renderer(example_processor=str.upper)

    class L:
        @staticmethod
        def legend():
            return {
                "element": "E",
                "description": "descr",
                "example": "foo",
            }

    out = lr.render([L])
    # строка содержит преобразованное «FOO» и элемент
    assert "FOO" in out and "E" in out
