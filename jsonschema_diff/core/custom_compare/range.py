# jsonschema_diff/custom_compare/range.py
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from ..abstraction import Statuses, ToCompare
from ..compare_combined import CompareCombined

if TYPE_CHECKING:
    from ..compare_base import LEGEND_RETURN_TYPE


Number = Union[int, float]
Dimension = Literal["value", "length", "items", "properties"]


@dataclass(frozen=True)
class Bounds:
    lower: Optional[Number]
    lower_inclusive: bool
    upper: Optional[Number]
    upper_inclusive: bool

    def is_empty(self) -> bool:
        return self.lower is None and self.upper is None


class CompareRange(CompareCombined):
    """
    Ranges for JSON Schema:
      - value:       minimum/maximum (+ exclusiveMinimum/Maximum: bool|number)
      - length:      minLength/maxLength
      - items:       minItems/maxItems
      - properties:  minProperties/maxProperties

    Notes:
      - bool is not considered a number (excluded from isinstance(int))
      - use only dict_compare (ToCompare by keys)
    """

    INFINITY = "∞"

    # ---- Жизненный цикл ----

    def compare(self) -> Statuses:
        super().compare()

        dimension = self._detect_dimension()
        old_b = self._bounds_for_side("old", dimension)
        new_b = self._bounds_for_side("new", dimension)

        if old_b.is_empty() and new_b.is_empty():
            self.status = Statuses.NO_DIFF
            return self.status
        if old_b.is_empty() and not new_b.is_empty():
            self.status = Statuses.ADDED
            return self.status
        if not old_b.is_empty() and new_b.is_empty():
            self.status = Statuses.DELETED
            return self.status

        if (
            old_b.lower == new_b.lower
            and old_b.upper == new_b.upper
            and old_b.lower_inclusive == new_b.lower_inclusive
            and old_b.upper_inclusive == new_b.upper_inclusive
        ):
            self.status = Statuses.NO_DIFF
        else:
            self.status = Statuses.REPLACED

        return self.status

    def get_name(self) -> str:
        dimension = self._detect_dimension()
        return self._key_for_dimension(dimension)

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        header = self._render_start_line(tab_level=tab_level, with_path=with_path)

        dimension = self._detect_dimension()
        if self.status in (Statuses.ADDED, Statuses.NO_DIFF):
            return f"{header} {self._format_bounds(self._bounds_for_side('new', dimension))}"
        if self.status is Statuses.DELETED:
            return f"{header} {self._format_bounds(self._bounds_for_side('old', dimension))}"

        old_repr = self._format_bounds(self._bounds_for_side("old", dimension))
        new_repr = self._format_bounds(self._bounds_for_side("new", dimension))
        return f"{header} {old_repr} -> {new_repr}"

    @staticmethod
    def legend() -> "LEGEND_RETURN_TYPE":
        return {
            "element": "Ranges",
            "description": (
                "Range - custom render for min/max/exclusiveMin/exclusiveMax fields, "
                "as well as all their analogues for strings/arrays/objects.\n\n"
                "[] - inclusive, () - exclusive\n"
                "∞ - infinity\n"
                "The principle is the same as it was taught in school."
            ),
            "example": [
                {
                    "old_value": {},
                    "new_value": {
                        "minimum": 1,
                        "maximum": 32,
                        "exclusiveMinimum": True,
                        "exclusiveMaximum": False,
                    },
                },
                {
                    "old_value": {"minProperties": 1},
                    "new_value": {"minProperties": 1, "maxProperties": 32},
                },
                {
                    "old_value": {"minItems": 1, "maxItems": 32},
                    "new_value": {},
                },
                {
                    "old_value": {"minLength": 1, "maxLength": 32},
                    "new_value": {"minLength": 5, "maxLength": 10},
                },
            ],
        }

    # ---- Определение измерения/ключа ----

    def _detect_dimension(self) -> Dimension:
        keys = set(self.dict_compare.keys())

        def has_any(*candidates: str) -> bool:
            return bool(keys.intersection(candidates))

        if has_any("minLength", "maxLength"):
            return "length"
        if has_any("minItems", "maxItems"):
            return "items"
        if has_any("minProperties", "maxProperties"):
            return "properties"
        return "value"

    @staticmethod
    def _key_for_dimension(dimension: Dimension) -> str:
        return {
            "value": "range",
            "length": "rangeLength",
            "items": "rangeItems",
            "properties": "rangeProperties",
        }[dimension]

    # ---- Извлечение значений (только через ToCompare) ----

    def _get_side_value(self, side: Literal["old", "new"], key: str) -> Any:
        tc: ToCompare | None = self.dict_compare.get(key)
        if tc is None:
            return None
        return tc.old_value if side == "old" else tc.new_value

    # ---- Построение границ ----

    def _bounds_for_side(self, side: Literal["old", "new"], dimension: Dimension) -> Bounds:
        if dimension == "value":
            return self._bounds_numbers(side)
        elif dimension == "length":
            return self._bounds_inclusive_pair(side, "minLength", "maxLength")
        elif dimension == "items":
            return self._bounds_inclusive_pair(side, "minItems", "maxItems")
        else:  # dimension == "properties"
            return self._bounds_inclusive_pair(side, "minProperties", "maxProperties")

    def _bounds_inclusive_pair(
        self, side: Literal["old", "new"], low_key: str, high_key: str
    ) -> Bounds:
        lower = self._as_number(self._get_side_value(side, low_key))
        upper = self._as_number(self._get_side_value(side, high_key))
        return Bounds(lower=lower, lower_inclusive=True, upper=upper, upper_inclusive=True)

    def _bounds_numbers(self, side: Literal["old", "new"]) -> Bounds:
        """
        Поддержка двух форматов exclusive*:
          - numeric (draft-06+): exclusiveMinimum/Maximum = number
          - boolean (старый):    exclusiveMinimum/Maximum = true/false вместе с minimum/maximum
        Приоритет у числового формата.
        """
        minimum = self._as_number(self._get_side_value(side, "minimum"))
        maximum = self._as_number(self._get_side_value(side, "maximum"))

        ex_min_raw = self._get_side_value(side, "exclusiveMinimum")
        ex_max_raw = self._get_side_value(side, "exclusiveMaximum")

        ex_min_num = self._as_number(ex_min_raw)
        ex_max_num = self._as_number(ex_max_raw)

        # нижняя граница
        lower: Number | None
        if ex_min_num is not None:
            lower = ex_min_num
            lower_inc = False
        elif isinstance(ex_min_raw, bool) and ex_min_raw and minimum is not None:
            lower = minimum
            lower_inc = False
        else:
            lower = minimum
            lower_inc = minimum is not None

        # верхняя граница
        upper: Number | None
        if ex_max_num is not None:
            upper = ex_max_num
            upper_inc = False
        elif isinstance(ex_max_raw, bool) and ex_max_raw and maximum is not None:
            upper = maximum
            upper_inc = False
        else:
            upper = maximum
            upper_inc = maximum is not None

        return Bounds(
            lower=lower,
            lower_inclusive=lower_inc,
            upper=upper,
            upper_inclusive=upper_inc,
        )

    @staticmethod
    def _as_number(value: object | None) -> Optional[Number]:
        # bool — подкласс int, исключаем
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
        return None

    # ---- Форматирование ----

    def _format_bounds(self, b: Bounds) -> str:
        left = "[" if b.lower is not None and b.lower_inclusive else "("
        right = "]" if b.upper is not None and b.upper_inclusive else ")"
        lo = str(b.lower) if b.lower is not None else f"-{self.INFINITY}"
        hi = str(b.upper) if b.upper is not None else self.INFINITY
        return f"{left}{lo} ... {hi}{right}"
