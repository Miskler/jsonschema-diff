from collections import OrderedDict
from typing import Any, Dict, List, Tuple

class Combiner:
    def __init__(
        self,
        rules: List[List[str]],
        inner_key_field: str | None = "comparator",
        inner_value_field: str | None = "to_compare",
    ):
        self.rules = rules
        self.inner_key_field = inner_key_field
        self.inner_value_field = inner_value_field

    def _require_inner_fields(self) -> None:
        if not self.inner_key_field or not self.inner_value_field:
            raise ValueError("inner_key_field и inner_value_field должны быть заданы.")

    def _extract(self, item: Any, key_name: str) -> Tuple[Any, Any]:
        """
        Возвращает (field, val) из элемента subset[key_name].
        Бросает TypeError, если структура не соответствует ожиданиям.
        """
        if not isinstance(item, dict):
            raise TypeError(f"Ожидался dict для '{key_name}', получено {type(item).__name__}")
        if self.inner_key_field not in item or self.inner_value_field not in item:
            raise TypeError(
                f"Элемент '{key_name}' должен содержать поля "
                f"'{self.inner_key_field}' и '{self.inner_value_field}'"
            )
        return item[self.inner_key_field], item[self.inner_value_field]

    def combine(self, subset: Dict[str, Any]) -> Dict[Tuple[str, ...], Dict[str, Any]]:
        """
        Возвращает OrderedDict:
          (k1, k2, ...) -> {
              inner_key_field: <общее значение ключа внутри группы>,
              inner_value_field: [v1, v2, ...]  # в порядке определения в правиле
          }
        Каждый список из rules образует свою группу (перекрытия допускаются).
        Ключи, не попавшие ни в одно правило, возвращаются одиночками.
        """
        self._require_inner_fields()
        out: "OrderedDict[Tuple[str, ...], Dict[str, Any]]" = OrderedDict()
        seen_in_rules: set[str] = set()

        # 1) группы по правилам
        for rule in self.rules:
            present = [k for k in rule if k in subset]
            if not present:
                continue

            # извлекаем значения в порядке правила
            fields: List[Any] = []
            vals: List[Any] = []
            for k in present:
                f, v = self._extract(subset[k], k)
                fields.append(f)
                vals.append(v)

            # проверяем一致ность inner_key внутри группы
            base_field = fields[0]
            for f in fields[1:]:
                if f != base_field:
                    raise ValueError(
                        f"Несовпадающий '{self.inner_key_field}' в группе {tuple(present)}: "
                        f"{base_field!r} vs {f!r}"
                    )

            out[tuple(present)] = {
                self.inner_key_field: base_field,
                self.inner_value_field: vals,
            }
            seen_in_rules.update(present)

        # 2) одиночки — в порядке появления во входном словаре
        for k, item in subset.items():
            if k in seen_in_rules:
                continue
            f, v = self._extract(item, k)
            out[(k,)] = {
                self.inner_key_field: f,
                self.inner_value_field: [v],
            }

        return out
