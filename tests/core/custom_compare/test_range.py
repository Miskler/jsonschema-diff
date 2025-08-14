import importlib
import pytest

# ------------------------------------------------------------
# Импортируем объект под тестом и вспомогательные типы
# ------------------------------------------------------------
CompareRange = importlib.import_module(
    "jsonschema_diff.core.custom_compare.range"
).CompareRange
abstraction   = importlib.import_module("jsonschema_diff.core.abstraction")
Statuses, ToCompare = abstraction.Statuses, abstraction.ToCompare


# ------------------------------------------------------------
# Мини-Config: ровно то, что использует RenderTool
# ------------------------------------------------------------
class DummyConfig:
    TAB = "  "
    PATH_MAKER_IGNORE: list[str] = []


# ------------------------------------------------------------
# Вспомогательный конструктор
# ------------------------------------------------------------
def make_compare_range(old: dict, new: dict):
    """
    Строит список `ToCompare` по объединению ключей `old` и `new`,
    создаёт CompareRange, вызывает .compare() и возвращает объект.
    """
    payload: list[ToCompare] = []
    for k in set(old) | set(new):
        payload.append(
            ToCompare(
                old_key=k if k in old else None,
                old_value=old.get(k),
                new_key=k if k in new else None,
                new_value=new.get(k),
            )
        )

    cmp = CompareRange(
        config=DummyConfig(),
        schema_path=[],
        json_path=[],
        to_compare=payload,
    )
    cmp.compare()
    return cmp


# =================================================================
#                           Т Е С Т Ы
# =================================================================
# ---------- util: _as_number -------------------------------------
@pytest.mark.parametrize(
    "raw, expected",
    [
        (5, 5),
        (3.14, 3.14),
        (True, None),          # bool исключается
        ("7", None),           # строка игнорируется
    ],
)
def test_as_number_filters(raw, expected):
    assert CompareRange._as_number(raw) == expected


# ---------- NO_DIFF ----------------------------------------------
def test_no_diff_identical_bounds():
    bounds = {"minimum": 1, "maximum": 5}
    cmp = make_compare_range(bounds, bounds)

    assert cmp.status is Statuses.NO_DIFF
    out = cmp.render(with_path=False)
    assert "[1 ... 5]" in out
    assert out.startswith("  ")          # префикс – два пробела



# ---------- ADDED -------------------------------------------------
def test_added_bounds():
    new = {"minimum": 0, "maximum": 10}
    cmp = make_compare_range({}, new)

    assert cmp.status is Statuses.ADDED
    out = cmp.render(with_path=False)
    assert "[0 ... 10]" in out
    assert out.lstrip().startswith("+")


# ---------- DELETED -----------------------------------------------
def test_deleted_bounds():
    old = {"minimum": -5, "maximum": 5}
    cmp = make_compare_range(old, {})

    assert cmp.status is Statuses.DELETED
    out = cmp.render(with_path=False)
    assert "[-5 ... 5]" in out
    assert out.lstrip().startswith("-")


# ---------- REPLACED ----------------------------------------------
def test_replaced_bounds():
    old = {"minimum": 1, "maximum": 5}
    new = {"minimum": 0, "maximum": 10}
    cmp = make_compare_range(old, new)

    assert cmp.status is Statuses.REPLACED
    out = cmp.render(with_path=False)
    assert "[1 ... 5]" in out and "[0 ... 10]" in out and "->" in out


# ---------- Exclusive (boolean) -----------------------------------
def test_exclusive_boolean():
    new = {"minimum": 1, "exclusiveMinimum": True}
    cmp = make_compare_range({}, new)

    out = cmp.render(with_path=False)
    # левая скобка должна быть «(», знак ∞ справа
    assert "(1 ... ∞)" in out or "(1 ... " in out


# ---------- Exclusive (numeric) -----------------------------------
def test_exclusive_numeric():
    new = {"exclusiveMinimum": 2, "exclusiveMaximum": 8}
    cmp = make_compare_range({}, new)

    out = cmp.render(with_path=False)
    assert "(2 ... 8)" in out


# ---------- Dimension detection (length) --------------------------
def test_dimension_length_and_get_name():
    new = {"minLength": 1, "maxLength": 3}
    cmp = make_compare_range({}, new)

    assert cmp.get_name() == "rangeLength"
    assert "[1 ... 3]" in cmp.render(with_path=False)
