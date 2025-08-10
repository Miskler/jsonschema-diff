from __future__ import annotations
from typing import Dict, List, Mapping, Sequence, Type, Union, Iterable, MutableMapping
from jsonschema_diff.core.parameter_base import Compare

# Тип ключа в правилах: имя параметра ИЛИ класс компаратора
RuleKey = Union[str, Type["Compare"]]


class RenderContextHandler:
    @staticmethod
    def resolve(
        *,
        pair_context_rules: Sequence[Sequence[RuleKey]],
        context_rules: Mapping[RuleKey, Sequence[RuleKey]],
        for_render: Mapping[str, Compare],
        not_for_render: Mapping[str, Compare],
    ) -> Dict[str, Compare]:
        """
        pair_context_rules: список «неориентированных» групп — если текущий ключ
            попал в группу, переносим остальных участников группы (по порядку записи группы).
            Элементы группы — строки (имена параметров) или классы компараторов.
        context_rules: ориентированные зависимости: source -> [targets...],
            где source и targets — строки или классы компараторов.

        for_render: {имя -> Compare} — триггер и базовый порядок вывода.
        not_for_render: {имя -> Compare} — то, что можно подтянуть как контекст.

        Возвращает упорядоченный dict {имя -> Compare} — тот же порядок, что на экране.
        """

        # Локальные копии, чтобы не мутировать вход
        out: Dict[str, Compare] = dict(for_render)          # сохраняет порядок
        pool_not: Dict[str, Compare] = dict(not_for_render) # сохраняет порядок вставки

        # Порядок обхода: сканируем имена, новые кандидаты добавляем в хвост
        seq: List[str] = list(out.keys())

        in_out = set(seq)  # быстрые проверки наличия в out

        def _matches(rule: RuleKey, name: str, cmp_obj: Compare) -> bool:
            if isinstance(rule, str):
                return rule == name
            # rule — класс компаратора
            try:
                return isinstance(cmp_obj, rule)  # type: ignore[arg-type]
            except TypeError:
                return False

        def _expand(rule: RuleKey, pool: Mapping[str, Compare]) -> Iterable[str]:
            """
            Преобразует элемент правила в список КЛЮЧЕЙ из pool (not_for_render),
            сохраняя порядок pool.
            - Если rule — строка: вернём [rule] если он есть в pool.
            - Если rule — класс компаратора: вернём все ключи в pool,
            чьи компараторы isinstance этого класса.
            """
            if isinstance(rule, str):
                if rule in pool:
                    # даже если pool потом мутируют — мы уже вернули конкретный ключ
                    yield rule
                return

            # правило — класс компаратора: берём снэпшот, чтобы не падать
            # при последующих del из pool_not во внешнем коде
            for n, obj in list(pool.items()):  # <-- Снэпшот!
                try:
                    if isinstance(obj, rule):  # type: ignore[arg-type]
                        yield n
                except TypeError:
                    continue


        i = 0
        while i < len(seq):
            name = seq[i]
            cmp_obj = out[name]

            # 1) Пары (неориентированные группы): если текущий участвует в группе — переносим остальных
            for group in pair_context_rules:
                if any(_matches(entry, name, cmp_obj) for entry in group):
                    for entry in group:
                        # для каждого элемента группы разворачиваем в кандидатов из pool_not
                        for cand in _expand(entry, pool_not):
                            if cand in in_out:
                                continue
                            # переносим cand из not -> out (в конец)
                            out[cand] = pool_not[cand]
                            seq.append(cand)
                            in_out.add(cand)
                            del pool_not[cand]

            # 2) Ориентированные зависимости: source(name/type) -> targets(...)
            for source, targets in context_rules.items():
                if _matches(source, name, cmp_obj):
                    for entry in targets:
                        for cand in _expand(entry, pool_not):
                            if cand in in_out:
                                continue
                            out[cand] = pool_not[cand]
                            seq.append(cand)
                            in_out.add(cand)
                            del pool_not[cand]

            i += 1

            # Новые элементы окажутся в хвосте seq и будут обработаны, когда до них дойдём.

        return out
