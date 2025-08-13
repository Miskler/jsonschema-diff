from typing import Sequence, List, Any, TypeAlias, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Config
    from ..abstraction import Statuses

PATH_MAKER_IGNORE_RULES_TYPE: TypeAlias = Sequence[str]

class RenderTool:
    @staticmethod
    def make_tab(config: "Config", tab_level: int) -> str:
        return config.TAB * tab_level
    
    @staticmethod
    def make_prefix(status: "Statuses") -> str:
        return f"{status.value}"

    @staticmethod
    def make_path(
        schema_path: Sequence[Any],
        json_path: Sequence[Any],
        ignore: PATH_MAKER_IGNORE_RULES_TYPE = ("properties",),
    ) -> str:
        """Собирает «читаемый» путь по двум параллельным спискам:

        * **schema_path** — токены, полученные при обходе JSON Schema;
        * **json_path**   — реальный путь в документе;
        * **ignore**      — служебные схемные слова, которые следует пропускать.

        Алгоритм
        ---------
        1. Идём двумя указателями *i* (схема) и *j* (JSON).
        2. Если текущий схемный токен входит в *ignore* и **не** совпадает с
        токеном JSON — просто пропускаем.
        3. Если токены совпали ⇒ выводим их как свойство или индекс и
        продвигаем оба указателя.
        4. Иначе токен присутствует только в схеме ⇒ выводим его как
        дополнительное свойство «.*token*» и двигаем *i*.
        5. После окончания *schema_path* дописываем оставшиеся элементы
        *json_path*.

        Числовые индексы (``int`` или строка из цифр) выводятся как ``[n]``
        без кавычек; остальные — как ``["key"]``.
        """
        parts: List[str] = []
        i = j = 0

        while i < len(schema_path):
            s_tok = schema_path[i]

            # 1. Игнорируемые схемные токены
            if s_tok in ignore and (
                j >= len(json_path) or str(s_tok) != str(json_path[j])
            ):
                i += 1
                continue

            # 2. Совпадение схемы и JSON
            if j < len(json_path) and str(s_tok) == str(json_path[j]):
                tok = json_path[j]
                parts.append(f"[{tok}]" if isinstance(tok, int) else f'["{tok}"]')
                i += 1
                j += 1
                continue

            # 3. Токен есть только в схеме – выводим как .key
            parts.append(f".{s_tok}")
            i += 1

        # 4. Добираем остаток json_path
        for tok in json_path[j:]:
            parts.append(f"[{tok}]" if isinstance(tok, int) else f'["{tok}"]')

        return "".join(parts)
