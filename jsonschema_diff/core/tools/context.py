from typing import Iterable, List, Dict, Sequence, DefaultDict
from collections import defaultdict

class RenderContextHandler:
    @staticmethod
    def resolve(
        *,
        pair_context_rules: Sequence[Sequence[str]],
        context_rules: Dict[str, Sequence[str]],
        for_render: Iterable[str],
        not_for_render: Iterable[str] = (),
    ) -> List[str]:
        """
        Алгоритм:
        1) Начинаем с копии for_render (это и триггер, и итоговый список).
        2) Итерируемся по этому списку слева направо (индекс i).
        3) Для текущего ключа k:
           3.1) Находим все группы из pair_context_rules, где встречается k,
                и по порядку элементов группы переносим недостающие ключи
                из not_for_render в конец результата.
           3.2) По context_rules[k] по порядку переносим недостающие ключи
                из not_for_render в конец результата.
        4) Когда i доходит до конца (с учётом новых хвостовых добавлений), завершаем.
        Порядок полностью определяется:
          - исходным порядком for_render,
          - порядком элементов в самих правилах,
          - порядком появления новых ключей при обходе.
        """

        # Итоговый список (сохраняем исходный порядок)
        out: List[str] = list(for_render)

        # Быстрые проверки наличия, НЕ задающие порядок:
        in_out = set(out)                      # что уже в out
        in_not = {k: idx for idx, k in enumerate(not_for_render)}  # что можем переносить

        # Предрасчёт: для каждого ключа — список групп (сохраняем порядок правил)
        groups_by_key: DefaultDict[str, List[Sequence[str]]] = defaultdict(list)
        for group in pair_context_rules:
            for k in group:
                groups_by_key[k].append(group)

        i = 0
        while i < len(out):
            k = out[i]

            # 3.1 Пары (неориентированные группы), обрабатываем группы в порядке их записи
            for group in groups_by_key.get(k, []):
                for cand in group:
                    if cand == k:
                        continue
                    if cand in in_not and cand not in in_out:
                        out.append(cand)
                        in_out.add(cand)
                        del in_not[cand]

            # 3.2 Ориентированные зависимости
            for cand in context_rules.get(k, ()):
                if cand in in_not and cand not in in_out:
                    out.append(cand)
                    in_out.add(cand)
                    del in_not[cand]

            i += 1

            # (никаких дополнительных проходов не нужно — новые элементы окажутся в хвосте
            #  и будут обработаны, когда до них дойдёт индекс i)

        return out

