from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Tuple

class Combiner:
    def __init__(self, 
                 rules: List[List[str]], 
                 inner_key_field: str | None = None, 
                 inner_value_field: str | None = None):
        self.rules = rules
        self.inner_key_field = inner_key_field
        self.inner_value_field = inner_value_field

    def _combine_group(self, items: List[str], subset: Dict[str, Any]) -> Tuple[Tuple[str, ...], Any]:
        """Собирает одну группу по списку ключей items, присутствующих в subset."""
        group_keys = tuple(k for k in items if k in subset)
        if not group_keys:
            return (), None

        # Если указаны поля для «склейки» вида {"field": ..., "val": ...}
        if self.inner_key_field and self.inner_value_field:
            # Берём «field» из первого, проверяем一致ность (жёстко; если не надо — смягчи)
            first = subset[group_keys[0]]
            base_field = first[self.inner_key_field]
            for k in group_keys[1:]:
                if subset[k][self.inner_key_field] != base_field:
                    raise ValueError(
                        f"Inconsistent '{self.inner_key_field}' in group {group_keys}: "
                        f"{base_field!r} vs {subset[k][self.inner_key_field]!r}"
                    )
            combined_vals = [subset[k][self.inner_value_field] for k in group_keys]
            result = {
                self.inner_key_field: base_field,
                self.inner_value_field: combined_vals,
            }
            return group_keys, result

        # Без специальных полей — просто собрать значения в список в порядке группы
        return group_keys, [subset[k] for k in group_keys]

    def combine(self, subset: Dict[str, Any]) -> Dict[Tuple[str, ...], Any]:
        """
        - Каждый список из rules даёт отдельную группу (возможны перекрытия по ключам).
        - Ключи, не попавшие ни в одно правило, идут одиночками.
        """
        out: "OrderedDict[Tuple[str, ...], Any]" = OrderedDict()
        seen_in_rules: set[str] = set()

        # 1) Группы по правилам
        for rule in self.rules:
            group_keys, payload = self._combine_group(rule, subset)
            if group_keys:
                out[group_keys] = payload
                seen_in_rules.update(group_keys)

        # 2) Одиночки: те, кто не встречался ни в одном правиле
        for k in subset:  # сохраняем порядок появления во входном словаре
            if k not in seen_in_rules:
                if self.inner_key_field and self.inner_value_field and isinstance(subset[k], dict):
                    # Привести к унифицированному виду {"field": ..., "val": [ ... ]}
                    single = subset[k]
                    single_field = single.get(self.inner_key_field, None)
                    single_val = single.get(self.inner_value_field, None)
                    out[(k,)] = {
                        self.inner_key_field: single_field,
                        self.inner_value_field: [single_val],
                    }
                else:
                    out[(k,)] = [subset[k]]

        return out
