from typing import Sequence

class PathRender:
    @staticmethod
    def make(
        schema_path: Sequence[str | int],
        json_path: Sequence[str | int],
        ignore: Sequence[str] = ("properties",),
    ) -> str:
        parts: list[str] = []
        i = j = 0

        while i < len(schema_path):
            tok_schema = schema_path[i]

            # 1. игнорируемые слова схемы
            if tok_schema in ignore:
                i += 1
                continue

            # 2. совпадение с JSON-путём
            if j < len(json_path) and str(tok_schema) == str(json_path[j]):
                if isinstance(tok_schema, int):
                    parts.append(f"[{tok_schema}]")
                else:
                    parts.append(f'["{tok_schema}"]')
                i += 1
                j += 1
                continue

            # 3. специальные схемные слова
            parts.append(f".{tok_schema}")
            i += 1

        # 4. добираем остатки json_path
        while j < len(json_path):
            tok_json = json_path[j]
            if isinstance(tok_json, int):
                parts.append(f"[{tok_json}]")
            else:
                parts.append(f'["{tok_json}"]')
            j += 1

        return "".join(parts)
