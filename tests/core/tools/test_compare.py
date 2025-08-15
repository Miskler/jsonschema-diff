from types import NoneType

from jsonschema_diff.core.tools import CompareRules


# ---------------------------------
# «Фейковые» классы-компараторы
# ---------------------------------
class DefaultCmp:
    pass


class KeyTripleCmp:
    pass


class KeyOnlyCmp:
    pass


class TypePairCmp:
    pass


class NewTypeCmp:
    pass


class OldTypeCmp:
    pass


def make_rules(*partials, **string_keys):
    """
    Собирает единый словарь правил из:
      * позиционных аргументов-словарей с любыми ключами;
      * обычных kwargs (строковые ключи).
    """
    merged: dict = {}
    for part in partials:
        merged.update(part)
    merged.update(string_keys)
    return merged


# ---------------------------------
# Тесты get_comparator
# ---------------------------------
def test_choose_by_key_old_new_triple():
    rules = make_rules(
        {("size", int, float): KeyTripleCmp},
        {"size": KeyOnlyCmp},  # не должен сработать
        {(int, float): TypePairCmp},  # не должен сработать
    )
    result = CompareRules.get_comparator(rules, DefaultCmp, key="size", old=int, new=float)
    assert result is KeyTripleCmp


def test_choose_by_key_only():
    rules = make_rules(
        {"size": KeyOnlyCmp},
        {(int, float): TypePairCmp},
    )
    result = CompareRules.get_comparator(rules, DefaultCmp, key="size", old=str, new=str)
    assert result is KeyOnlyCmp


def test_choose_by_type_pair():
    rules = make_rules({(int, float): TypePairCmp})
    result = CompareRules.get_comparator(rules, DefaultCmp, key="other", old=int, new=float)
    assert result is TypePairCmp


def test_fallback_old_is_NoneType_uses_new_type_rule():
    rules = make_rules({str: NewTypeCmp})
    result = CompareRules.get_comparator(rules, DefaultCmp, key="x", old=NoneType, new=str)
    assert result is NewTypeCmp


def test_fallback_old_not_NoneType_uses_old_type_rule():
    rules = make_rules({float: OldTypeCmp})
    result = CompareRules.get_comparator(rules, DefaultCmp, key="y", old=float, new=int)
    assert result is OldTypeCmp


def test_no_rule_returns_default():
    result = CompareRules.get_comparator(rules={}, default=DefaultCmp, key="k", old=int, new=int)
    assert result is DefaultCmp


# ---------------------------------
# Тесты get_comparator_from_values
# ---------------------------------
def test_from_values_converts_to_types():
    rules = make_rules({(int, float): TypePairCmp})
    # передаём сами значения, функция возьмёт их типы
    result = CompareRules.get_comparator_from_values(
        rules, DefaultCmp, key="irrelevant", old=1, new=1.0
    )
    assert result is TypePairCmp
