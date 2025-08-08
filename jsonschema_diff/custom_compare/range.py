from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, TypedDict

from ..abstraction import Statuses, ToCompare
from ..parameter_combined import CompareCombined

Dimension = Literal["value", "length", "items", "properties"]

@dataclass(frozen=True)
class Bounds:
    lower: Optional[float | int]
    lower_inclusive: bool
    upper: Optional[float | int]
    upper_inclusive: bool

class CompareRange(CompareCombined):
    """
    Единый компаратор «диапазонов»:
      value: minimum / maximum / exclusiveMinimum / exclusiveMaximum
      length: minLength / maxLength
      items: minItems / maxItems
      properties: minProperties / maxProperties

    Внутри нормализует до Bounds и печатает:
      .range*: [a ... b), [a ... ∞), (-∞ ... b], ...
    """

    # --- Публичное API -----------------------------------------------------

    def compare(self) -> Statuses:
        # Базовая агрегация статусов полей в одну сущность
        status = super().compare()
        if status == Statuses.MODIFIED:
            # По твоим правилам — считаться не должен
            raise ValueError("CompareRange: unsupported status MODIFIED")
        return status

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        dimension = self._detect_dimension()
        self.key = self._key_for_dimension(dimension)  # range/rangeLength/...

        prefix = self._render_start_line(tab_level=tab_level, with_path=with_path)

        if self.status in (Statuses.ADDED, Statuses.NO_DIFF):
            return f"{prefix} {self._format_bounds(self._bounds_for_side('new', dimension))}"
        if self.status == Statuses.DELETED:
            return f"{prefix} {self._format_bounds(self._bounds_for_side('old', dimension))}"
        if self.status == Statuses.REPLACED:
            old_repr = self._format_bounds(self._bounds_for_side('old', dimension))
            new_repr = self._format_bounds(self._bounds_for_side('new', dimension))
            return f"{prefix} {old_repr} -> {new_repr}"

        raise ValueError(f"CompareRange: unsupported status {self.status}")

    # --- Вспомогательные ---------------------------------------------------

    def _detect_dimension(self) -> Dimension:
        keys = set(self.dict_compare.keys())
        if {"minLength", "maxLength"} & keys:
            return "length"
        if {"minItems", "maxItems"} & keys:
            return "items"
        if {"minProperties", "maxProperties"} & keys:
            return "properties"
        # по умолчанию считаем числовой диапазон по значению
        return "value"

    @staticmethod
    def _key_for_dimension(dimension: Dimension) -> str:
        return {
            "value": "range",
            "length": "rangeLength",
            "items": "rangeItems",
            "properties": "rangeProperties",
        }[dimension]

    def _get_side_value(self, key: str, side: Literal["old", "new"]) -> object | None:
        tc: ToCompare | None = self.dict_compare.get(key)
        if tc is None:
            return None
        return tc.old_value if side == "old" else tc.new_value

    # ---- нормализация границ ---------------------------------------------

    def _bounds_for_side(self, side: Literal["old", "new"], dimension: Dimension) -> Bounds:
        if dimension == "value":
            return self._bounds_value(side)
        if dimension == "length":
            return self._bounds_inclusive_pair(side, "minLength", "maxLength")
        if dimension == "items":
            return self._bounds_inclusive_pair(side, "minItems", "maxItems")
        if dimension == "properties":
            return self._bounds_inclusive_pair(side, "minProperties", "maxProperties")
        # защита от будущих расширений
        raise ValueError(f"Unknown dimension: {dimension}")

    def _bounds_inclusive_pair(self, side: Literal["old", "new"], lo_key: str, hi_key: str) -> Bounds:
        lower = self._get_numeric(self._get_side_value(lo_key, side))
        upper = self._get_numeric(self._get_side_value(hi_key, side))
        return Bounds(lower=lower, lower_inclusive=True, upper=upper, upper_inclusive=True)

    def _bounds_value(self, side: Literal["old", "new"]) -> Bounds:
        """
        Поддерживает оба варианта exclusive*:
          - draft-07: exclusiveMinimum: true/false + minimum
          - 2019-09/2020-12: exclusiveMinimum: number (взаимоисключимо с minimum)
        Конфликт при одновременном задании minimum и exclusiveMinimum(число)
        решаем в пользу exclusive* как более специфичного.
        """
        minimum = self._get_numeric(self._get_side_value("minimum", side))
        maximum = self._get_numeric(self._get_side_value("maximum", side))
        exclusive_min = self._get_side_value("exclusiveMinimum", side)
        exclusive_max = self._get_side_value("exclusiveMaximum", side)

        # lower
        if isinstance(exclusive_min, (int, float)):
            lower, lower_inclusive = exclusive_min, False
        elif exclusive_min is True:
            lower, lower_inclusive = minimum, False
        else:
            lower, lower_inclusive = minimum, True

        # upper
        if isinstance(exclusive_max, (int, float)):
            upper, upper_inclusive = exclusive_max, False
        elif exclusive_max is True:
            upper, upper_inclusive = maximum, False
        else:
            upper, upper_inclusive = maximum, True

        return Bounds(lower=lower, lower_inclusive=lower_inclusive,
                      upper=upper, upper_inclusive=upper_inclusive)

    @staticmethod
    def _get_numeric(value: object | None) -> float | int | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        # на всякий случай — JSON может принести число строкой
        try:
            return int(value) if str(value).isdigit() else float(str(value))
        except Exception:
            return None

    # ---- форматирование ---------------------------------------------------

    @staticmethod
    def _format_bounds(bounds: Bounds) -> str:
        inf = "∞"
        left_bracket = "[" if bounds.lower is not None and bounds.lower_inclusive else "("
        right_bracket = "]" if bounds.upper is not None and bounds.upper_inclusive else ")"
        lower_text = str(bounds.lower) if bounds.lower is not None else f"-{inf}"
        upper_text = str(bounds.upper) if bounds.upper is not None else inf
        return f"{left_bracket}{lower_text} ... {upper_text}{right_bracket}"
