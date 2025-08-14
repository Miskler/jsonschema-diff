import pytest
from collections import OrderedDict

from jsonschema_diff.core.tools import LogicCombinerHandler


# ---------------------------
# Вспомогательные фабрики
# ---------------------------
def make_item(comp, val, key="comparator", value="to_compare"):
    """Создаёт элемент словаря subset с указанными полями."""
    return {key: comp, value: val}


# ---------------------------
# Тесты _extract
# ---------------------------
def test_extract_success():
    item = make_item("size", 42)
    field, val = LogicCombinerHandler._extract(item, "foo", "comparator", "to_compare")
    assert (field, val) == ("size", 42)


@pytest.mark.parametrize(
    "bad_item",
    [
        123,                        # не-dict
        {"comparator": "x"},        # нет to_compare
        {"to_compare": 1},          # нет comparator
    ],
)
def test_extract_type_errors(bad_item):
    with pytest.raises(TypeError):
        LogicCombinerHandler._extract(bad_item, "foo", "comparator", "to_compare")


# ---------------------------
# Тесты combine — happy path
# ---------------------------
def test_combine_group_and_singles():
    """
    Проверяем:
      * группировку по правилу,
      * порядок: сначала группы по rules, затем одиночки в порядке входного subset.
    """
    subset = OrderedDict(
        [
            ("a", make_item("grp", 1)),
            ("b", make_item("grp", 2)),
            ("c", make_item("solo", 3)),
            ("d", make_item("other", 4)),
        ]
    )
    rules = [["b", "a"]]      # порядок в правиле важен

    result = LogicCombinerHandler.combine(subset, rules)

    exp = OrderedDict(
        [
            (("b", "a"), {"comparator": "grp", "to_compare": [2, 1]}),
            (("c",), {"comparator": "solo", "to_compare": [3]}),
            (("d",), {"comparator": "other", "to_compare": [4]}),
        ]
    )
    assert result == exp


def test_combine_rule_with_missing_keys_is_ignored():
    """Правило без присутствующих ключей должно быть пропущено без ошибки."""
    subset = {"x": make_item("grp", 1)}
    rules = [["absent_1", "absent_2"]]

    result = LogicCombinerHandler.combine(subset, rules)

    assert list(result) == [("x",)]                 # только одиночка
    assert result[("x",)]["to_compare"] == [1]


def test_combine_custom_field_names():
    subset = {"k": {"field": "F", "value": 7}}
    out = LogicCombinerHandler.combine(
        subset,
        rules=[],
        inner_key_field="field",
        inner_value_field="value",
    )
    assert out == {("k",): {"field": "F", "value": [7]}}


# ---------------------------
# Тесты combine — ошибки
# ---------------------------
def test_combine_mismatched_inner_key_raises():
    subset = {
        "p": make_item("one", 1),
        "q": make_item("two", 2),
    }
    with pytest.raises(ValueError, match="Несовпадающий"):
        LogicCombinerHandler.combine(subset, [["p", "q"]])


def test_combine_missing_inner_fields_raises():
    subset = {}
    with pytest.raises(ValueError, match="должны быть заданы"):
        LogicCombinerHandler.combine(subset, [], inner_key_field=None, inner_value_field=None)
