
from typing import Any, Dict, Hashable, Iterable, Mapping, Tuple, Union, Optional

class _DSU:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def _add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        self._add(x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


class Combiner:
    """
    Быстрый комбинировщик значений по правилам совместимости ключей.

    Формат входных данных метода combine:
        items = {
            combo_key1: {inner_key_field: "K", inner_value_field: v1},
            combo_key2: {inner_key_field: "K", inner_value_field: v2},
            ...
        }

    Возвращает:
        {"K": [v1, v2, ...]} — порядок значений соответствует порядку ключей в `items`.

    Ошибки:
      * Если передали ключи из разных компонент (их нельзя комбинировать) — ValueError.
      * Если у комбинируемых записей отличается внутренний ключ — ValueError.

    Параметры конструктора:
      - rules: описание правил. Поддерживаются форматы:
          * Iterable[Iterable[K]]      -> каждая вложенная коллекция — группа (компонента).
          * Mapping[K, Iterable[K]]    -> ребра (k соединён со всеми из iterable).
          * Iterable[Tuple[K, K]]      -> список пар-ребер.
      - inner_key_field: имя поля с «внутренним ключом» (по умолчанию "key").
      - inner_value_field: имя поля со значением (по умолчанию "value").
    """

    def __init__(
        self,
        rules: Union[
            Iterable[Iterable[Hashable]],
            Mapping[Hashable, Iterable[Hashable]],
            Iterable[Tuple[Hashable, Hashable]],
        ],
        *,
        inner_key_field: str = "comparator",
        inner_value_field: str = "to_compare",
    ):
        self.inner_key_field = inner_key_field
        self.inner_value_field = inner_value_field
        self._dsu = _DSU()
        self._all_keys = set()
        self._ingest_rules(rules)

    def _ingest_rules(
        self,
        rules: Union[
            Iterable[Iterable[Hashable]],
            Mapping[Hashable, Iterable[Hashable]],
            Iterable[Tuple[Hashable, Hashable]],
        ],
    ):
        # Нормализуем в список ребер, затем склеим DSU
        edges: list[Tuple[Hashable, Hashable]] = []

        if isinstance(rules, Mapping):
            for a, bs in rules.items():
                self._dsu._add(a)
                self._all_keys.add(a)
                for b in bs:
                    edges.append((a, b))
                    self._all_keys.add(b)
                    self._dsu._add(b)
        else:
            # distinguish between iterable of pairs vs iterable of groups
            peeked: Optional[Any] = None
            it = iter(rules)
            try:
                peeked = next(it)
            except StopIteration:
                peeked = None

            def is_pair(x):
                return isinstance(x, tuple) and len(x) == 2

            if peeked is None:
                pass
            elif is_pair(peeked):
                # iterable of pairs
                a, b = peeked
                edges.append((a, b))
                self._all_keys.update([a, b])
                self._dsu._add(a)
                self._dsu._add(b)
                for a, b in it:  # type: ignore
                    edges.append((a, b))
                    self._all_keys.update([a, b])
                    self._dsu._add(a)
                    self._dsu._add(b)
            else:
                # iterable of groups
                group = peeked
                group = list(group)  # in case it's a generator
                for x in group:
                    self._all_keys.add(x)
                    self._dsu._add(x)
                for grp in [group, *[list(g) for g in it]]:  # type: ignore
                    for i in range(1, len(grp)):
                        edges.append((grp[0], grp[i]))
                        self._dsu._add(grp[i])
                        self._all_keys.add(grp[i])

        for a, b in edges:
            self._dsu.union(a, b)

    def _root(self, k: Hashable) -> Hashable:
        return self._dsu.find(k)

    def combine(self, items):
        """
        Разбивает items на группы по DSU и для каждой группы возвращает:
        { tuple(ключей_в_порядке_входа): {inner_key_field: <ik>, inner_value_field: [values...] } }
        Ключи, отсутствующие в rules, считаются синглтонами.
        """
        if not items:
            return {}

        # 1) разбить по компонентам (в порядке входа)
        groups = {}  # root -> [keys]
        for k in items:
            r = self._root(k)  # незнакомые ключи станут синглтонами
            groups.setdefault(r, []).append(k)

        # 2) собрать результат по каждой группе + валидация inner_key
        out = {}
        for keys in groups.values():
            inner_keys = set()
            values = []
            for k in keys:
                payload = items[k]
                try:
                    ik = payload[self.inner_key_field]
                    val = payload[self.inner_value_field]
                except KeyError as e:
                    missing = e.args[0]
                    raise KeyError(f"В записи для '{k}' отсутствует поле '{missing}'") from e
                inner_keys.add(ik)
                values.append(val)

            if len(inner_keys) != 1:
                raise ValueError(
                    f"В группе {tuple(keys)} обнаружены разные внутренние ключи: {inner_keys}"
                )

            ik = next(iter(inner_keys))
            out[tuple(keys)] = {
                self.inner_key_field: ik,
                self.inner_value_field: values,
            }

        return out


