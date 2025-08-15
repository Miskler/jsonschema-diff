from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING, Any, TypeAlias, cast

if TYPE_CHECKING:  # prevents import cycle
    from .. import Compare


COMPARE_RULES_TYPE: TypeAlias = dict[
    type | tuple[type, type] | str | tuple[str, type, type] | tuple[str, type],
    type["Compare"],
]
"""Mapping *search pattern* → *Compare* subclass."""


class CompareRules:
    """Pick an appropriate comparator class according to rule precedence."""

    # ------------------------------------------------------------------ #
    # Public helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_comparator_from_values(
        rules: COMPARE_RULES_TYPE,
        default: type["Compare"],
        key: str,
        old: Any,
        new: Any,
    ) -> type["Compare"]:
        """Wrapper that resolves comparator from **values**."""
        return CompareRules.get_comparator(rules, default, key, type(old), type(new))

    @staticmethod
    def get_comparator(
        rules: COMPARE_RULES_TYPE,
        default: type["Compare"],
        key: str,
        old: type,
        new: type,
    ) -> type["Compare"]:
        """
        Resolve a comparator class according to the following lookup order:

        1. ``(key, old_type, new_type)``
        2. ``key``
        3. ``(old_type, new_type)``
        4. ``old_type`` or ``new_type`` (if one of them is ``NoneType``)
        5. *default*

        Parameters
        ----------
        rules : dict
            Precedence map.
        default : Compare subclass
            Fallback comparator.
        key : str
            Field name.
        old, new : type
            Types being compared.
        """
        for search in [
            ((key, old, new)),
            (key),
            ((old, new)),
        ]:
            tuple_types = rules.get(cast(Any, search), None)
            if tuple_types is not None:
                return tuple_types
        else:
            if old is NoneType:
                return rules.get(new, default)
            elif old is not NoneType or old is new:
                return rules.get(old, default)
            else:
                return default
