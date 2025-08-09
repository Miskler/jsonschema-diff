# jsonschema_diff/custom_compare/range.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Union

from ..abstraction import Statuses, ToCompare
from ..parameter_combined import CompareCombined

Number = Union[int, float]
Dimension = Literal["value", "length", "items", "properties"]


@dataclass(frozen=True)
class Bounds:
    lower: Optional[Number]
    lower_inclusive: bool
    upper: Optional[Number]
    upper_inclusive: bool


class CompareRange(CompareCombined):
    """
    Комбинированный компаратор «диапазонов»:

      value       → minimum / maximum / exclusiveMinimum / exclusiveMaximum
      length      → minLength / maxLength
      items       → minItems / maxItems
      properties  → minProperties / maxProperties

    Нормализует ограничения в Bounds и печатает:
      .range*: [a ... b), [a ... ∞), (-∞ ... b], ...

    Статус определяется по Bounds (а не по агрегированию статусов детей):
      - NO_DIFF   — Bounds равны
      - ADDED     — old пуст, new непуст
      - DELETED   — old непуст, new пуст
      - REPLACED  — иначе
    """

    INFINITY = "∞"

    # ------------------------------ Публичный API ------------------------------

    def compare(self) -> Statuses:
        """
        ВАЖНО: сперва базовый compare() — наполняет dict_compare.
        Затем вычисляем Bounds для old/new и переопределяем self.status.
        """
        super().compare()

        dimension = self._detect_dimension()
        old_b = self._bounds_for_side("old", dimension)
        new_b = self._bounds_for_side("new", dimension)

        def empty(b: Bounds) -> bool:
            return b.lower is None and b.upper is None

        if old_b == new_b:
            self.status = Statuses.NO_DIFF
        elif empty(old_b) and not empty(new_b):
            self.status = Statuses.ADDED
        elif not empty(old_b) and empty(new_b):
            self.status = Statuses.DELETED
        else:
            self.status = Statuses.REPLACED

        return self.status

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        """
        Рендер строго по правилам:
          - ADDED/NO_DIFF → печатаем NEW
          - DELETED       → печатаем OLD
          - REPLACED      → OLD -> NEW
        """
        dimension = self._detect_dimension()
        self.key = self._key_for_dimension(dimension)

        header = self._render_start_line(tab_level=tab_level, with_path=with_path)

        if self.status in (Statuses.ADDED, Statuses.NO_DIFF):
            return f"{header} {self._format_bounds(self._bounds_for_side('new', dimension))}"
        if self.status == Statuses.DELETED:
            return f"{header} {self._format_bounds(self._bounds_for_side('old', dimension))}"
        if self.status == Statuses.REPLACED:
            old_repr = self._format_bounds(self._bounds_for_side("old", dimension))
            new_repr = self._format_bounds(self._bounds_for_side("new", dimension))
            return f"{header} {old_repr} -> {new_repr}"

        raise ValueError(f"CompareRange: unsupported status {self.status}")

    # ------------------------------ Внутренняя логика ------------------------------

    def _detect_dimension(self) -> Dimension:
        """
        Определяем измерение по ключам, попавшим в группу комбинатора.
        """
        keys = set(self.dict_compare.keys())
        if {"minLength", "maxLength"} & keys:
            return "length"
        if {"minItems", "maxItems"} & keys:
            return "items"
        if {"minProperties", "maxProperties"} & keys:
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

    # ---- Доступ к значениям нужной стороны (old/new) из ToCompare ----

    def _get_side_value(self, key: str, side: Literal["old", "new"]) -> Optional[object]:
        """
        Берём значение НУЖНОЙ стороны из ToCompare.
        НЕ используем tc.value (при REPLACED это всегда new).
        Фолбэков к self.old_value/self.new_value НЕТ — опираемся на dict_compare,
        который у тебя уже «полноценный» (есть и NO_DIFF).
        """
        tc: ToCompare | None = self.dict_compare.get(key)
        if tc is None:
            return None
        return tc.old_value if side == "old" else tc.new_value

    # ---- Построение границ для стороны ----

    def _bounds_for_side(self, side: Literal["old", "new"], dimension: Dimension) -> Bounds:
        if dimension == "value":
            return self._bounds_numbers(side)
        if dimension == "length":
            return self._bounds_inclusive_pair(side, "minLength", "maxLength")
        if dimension == "items":
            return self._bounds_inclusive_pair(side, "minItems", "maxItems")
        if dimension == "properties":
            return self._bounds_inclusive_pair(side, "minProperties", "maxProperties")
        raise ValueError(f"Unknown dimension: {dimension}")

    def _bounds_inclusive_pair(self, side: Literal["old", "new"], low_key: str, high_key: str) -> Bounds:
        lower = self._as_number(self._get_side_value(low_key, side))
        upper = self._as_number(self._get_side_value(high_key, side))
        return Bounds(lower=lower, lower_inclusive=True, upper=upper, upper_inclusive=True)

    def _bounds_numbers(self, side: Literal["old", "new"]) -> Bounds:
        """
        Числа: поддерживаем оба стиля exclusive*:
          - draft-07: exclusiveMinimum/Maximum: bool + minimum/maximum
          - 2019-09/2020-12: exclusiveMinimum/Maximum: number
        Конфликт «оба заданы» — приоритет у exclusive* (число).
        """
        minimum = self._as_number(self._get_side_value("minimum", side))
        maximum = self._as_number(self._get_side_value("maximum", side))
        ex_min = self._get_side_value("exclusiveMinimum", side)
        ex_max = self._get_side_value("exclusiveMaximum", side)

        # lower
        if isinstance(ex_min, (int, float)):
            lower, lower_inc = ex_min, False
        elif ex_min is True and minimum is not None:
            lower, lower_inc = minimum, False
        else:
            lower, lower_inc = minimum, True

        # upper
        if isinstance(ex_max, (int, float)):
            upper, upper_inc = ex_max, False
        elif ex_max is True and maximum is not None:
            upper, upper_inc = maximum, False
        else:
            upper, upper_inc = maximum, True

        return Bounds(lower=lower, lower_inclusive=lower_inc,
                      upper=upper, upper_inclusive=upper_inc)

    def _is_number(self, x): 
        return isinstance(x, (int, float)) and not isinstance(x, bool)

    def _as_number(self, value) -> Optional[Number]:
        return value if self._is_number(value) else None

    # ---- Форматирование ----

    def _format_bounds(self, b: Bounds) -> str:
        left = "[" if b.lower is not None and b.lower_inclusive else "("
        right = "]" if b.upper is not None and b.upper_inclusive else ")"
        lo = str(b.lower) if b.lower is not None else f"-{self.INFINITY}"
        hi = str(b.upper) if b.upper is not None else self.INFINITY
        return f"{left}{lo} ... {hi}{right}"
