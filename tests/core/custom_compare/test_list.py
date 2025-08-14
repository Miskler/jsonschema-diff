import importlib
import pytest

# ---------------------------------
# Импортируем тестируемый модуль
# ---------------------------------
from jsonschema_diff.core.custom_compare.list import CompareList, CompareListElement
from jsonschema_diff.core.abstraction import Statuses, ToCompare


# ---------------------------------
# Мини-Config для рендера
# ---------------------------------
class DummyConfig:
    """Достаточно TAB и PATH_MAKER_IGNORE для методов RenderTool."""
    def __init__(self, tab: str = "  "):
        self.TAB = tab
        self.PATH_MAKER_IGNORE = []


# ---------------------------------
# Вспомогательная фабрика
# ---------------------------------
def make_compare_list(old, new, key="myList"):
    """
    Создаёт CompareList, сразу вызывает .compare() и возвращает объект.
    old / new могут быть None.
    """
    tc = ToCompare(
        old_key=key if old is not None else None,
        old_value=old,
        new_key=key if new is not None else None,
        new_value=new,
    )
    cmp = CompareList(
        config=DummyConfig(),
        schema_path=[],
        json_path=[],
        to_compare=[tc],
    )
    cmp.compare()
    return cmp


# =================================================================
#                      Т Е С Т Ы   С Ц Е Н А Р И Е В
# =================================================================
# --- NO-DIFF -----------------------------------------------------
def test_no_diff_equal_lists():
    lst = [1, 2, 3]
    cmp = make_compare_list(lst, lst)

    assert cmp.status is Statuses.NO_DIFF
    assert cmp.elements == []
    assert cmp.changed_elements == []
    assert cmp.is_for_rendering() is False

    rendered = cmp.render(with_path=False)
    # префикс для NO_DIFF – одиночный пробел
    assert rendered.startswith("  ")
    # есть имя поля и завершающий «:», но без значения
    assert ".myList:" in rendered and rendered.strip().endswith(":")



# --- ADDED -------------------------------------------------------
def test_added_list():
    new = ["A", "B"]
    cmp = make_compare_list(None, new)
    assert cmp.status is Statuses.ADDED
    assert [e.status for e in cmp.elements] == [Statuses.ADDED] * len(new)
    assert cmp.changed_elements == cmp.elements
    assert cmp.is_for_rendering() is True

    lines = cmp.render(with_path=False).splitlines()
    assert len(lines) == 1 + len(new)      # шапка + элементы
    assert all(l.lstrip().startswith("+") for l in lines[1:])


# --- DELETED -----------------------------------------------------
def test_deleted_list():
    old = [1, 2]
    cmp = make_compare_list(old, None)
    assert cmp.status is Statuses.DELETED
    assert [e.status for e in cmp.elements] == [Statuses.DELETED] * len(old)

    lines = cmp.render(with_path=False).splitlines()
    assert len(lines) == 1 + len(old)
    assert all(l.lstrip().startswith("-") for l in lines[1:])


# --- MODIFIED (insert) ------------------------------------------
def test_modified_list_insertion():
    old = ["A", "B", "C"]
    new = ["A", "B", "C", "D"]          # вставка элемента
    cmp = make_compare_list(old, new)
    assert cmp.status is Statuses.MODIFIED

    added = [e for e in cmp.elements if e.status is Statuses.ADDED]
    assert len(added) == 1 and added[0].value == "D"

    unchanged = [e for e in cmp.elements if e.status is Statuses.NO_DIFF]
    assert [e.value for e in unchanged] == ["A", "B", "C"]
    assert cmp.changed_elements == added
    assert cmp.is_for_rendering() is True


# --- MODIFIED (replace) -----------------------------------------
def test_modified_list_replace_middle():
    old = ["A", "B", "C"]
    new = ["A", "X", "B", "C"]          # A ==, X +, B ==, C ==
    cmp = make_compare_list(old, new)
    assert cmp.status is Statuses.MODIFIED

    expected = [Statuses.NO_DIFF, Statuses.ADDED, Statuses.NO_DIFF, Statuses.NO_DIFF]
    assert [e.status for e in cmp.elements] == expected
    assert len(cmp.changed_elements) == 1 and cmp.changed_elements[0].value == "X"


# --- Legend ------------------------------------------------------
def test_legend_has_required_keys():
    legend = CompareList.legend()
    assert isinstance(legend, dict)
    assert {"element", "description", "example"} <= legend.keys()
