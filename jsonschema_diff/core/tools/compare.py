from __future__ import annotations
from typing import Any, TypeAlias, TYPE_CHECKING
from types import NoneType

if TYPE_CHECKING:
    from .. import Compare


COMPARE_RULES_TYPE: TypeAlias = dict[
      type 
    | tuple[type, type] 
    | str 
    | tuple[str, type, type] 
    | tuple[str, type],

    type["Compare"]
]

class CompareRules:
    @staticmethod
    def get_comparator_from_values(
        rules: COMPARE_RULES_TYPE,
        default: type["Compare"],
        key: str,
        old: Any,
        new: Any,
    ) -> type["Compare"]:
        return CompareRules.get_comparator(rules, default, key, type(old), type(new))

    @staticmethod
    def get_comparator(
        rules: COMPARE_RULES_TYPE,
        default: type["Compare"],
        key: str,
        old: type,
        new: type,
    ) -> type["Compare"]:
        # (ключ, старое, новое)
        # (ключ)
        # (старое, новое)
        # (общий валидный тип)
        # -> по умолчанию
        for search in [
            ((key, old, new)),
            (key),
            ((old, new)),
        ]:
            tuple_types = rules.get(search, None)
            if tuple_types is not None:
                return tuple_types
        else:
            if old is NoneType:
                return rules.get(new, default)
            elif old is not NoneType or old is new:
                return rules.get(old, default)
            else:
                return default
