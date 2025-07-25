"""
Модуль для сравнения JSON-схем и красивого отображения различий.
"""
from typing import Any, Dict, List, Tuple, Optional
import json
import click
from . import cfg as CONFIG


class SchemaComparator:
    """Внутренний класс для сравнения схем."""

    def __init__(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        self.old_schema = old_schema
        self.new_schema = new_schema

    def compare(self) -> str:
        """Выполняет сравнение схем и возвращает отформатированный результат."""
        differences = self._find_differences(
            {"properties": self.old_schema.get("properties", {})},
            {"properties": self.new_schema.get("properties", {})}
        )
        return self._format_differences(differences)

    def _format_output(self, text: str, mode: str = "no_diff") -> str:
        """Форматирует вывод с помощью Click."""
        return click.style(f'{CONFIG.modes[mode]["symbol"]} {text}', fg=CONFIG.modes[mode]["color"], bold=True)

    def _find_differences(
        self, old: Any, new: Any, path: Optional[List[str]] = None
    ) -> List[Tuple[List[str], Any, Any]]:
        """Рекурсивно находит различия между двумя структурами."""
        if path is None:
            path = []
        diffs: List[Tuple[List[str], Any, Any]] = []

        # Сравнение списков
        if isinstance(old, list) and isinstance(new, list):
            if old != new:
                diffs.append((path, old, new))
            return diffs

        # Сравнение словарей
        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            current_path = path + [key]
            if key not in old:
                diffs.append((current_path, None, new[key]))
            elif key not in new:
                diffs.append((current_path, old[key], None))
            else:
                ov = old[key]
                nv = new[key]
                if isinstance(ov, dict) and isinstance(nv, dict):
                    diffs.extend(self._find_differences(ov, nv, current_path))
                elif isinstance(ov, list) and isinstance(nv, list):
                    if ov != nv:
                        diffs.append((current_path, ov, nv))
                elif ov != nv:
                    diffs.append((current_path, ov, nv))
        return diffs

    @staticmethod
    def _format_path(path: List[str]) -> str:
        """Форматирует путь к изменению, пропуская 'properties' и 'items', сокращая .type и .required."""
        segments: List[str] = []
        for i, p in enumerate(path):
            if p in ("properties", "items"):
                continue
            # одинаковое условие для type и required
            if p in ("type", "required", "format", "additionalProperties", "anyOf") and (i == 0 or path[i-1] != "properties"):
                segments.append(f".{p}")
            else:
                segments.append(f"[{json.dumps(p, ensure_ascii=False)}]")
        return ''.join(segments)

    def _format_list_diff(self, path: str, old_list: List[Any] | None, new_list: List[Any] | None) -> List[str]:
        """Форматирует diff для списков: полный список с пометками +/-."""
        target_mode = "no_diff"

        if old_list is None:
            target_mode = "append"
            old_list = []
        elif new_list is None:
            target_mode = "remove"
            new_list = []

        result: List[str] = [self._format_output(f"{path}:", target_mode)]


        # Собираем все уникальные элементы без хеширования:
        unique_items: List[Any] = []
        for item in new_list + old_list:
            if not any(item == existing for existing in unique_items):
                unique_items.append(item)

        have_changes = False
        for item in unique_items:
            item_str = json.dumps(item, ensure_ascii=False)
            in_old = any(item == old for old in old_list)
            in_new = any(item == new for new in new_list)

            if in_old and not in_new:
                result.append(self._format_output(f"  {item_str},", "remove"))
                have_changes = True
            elif not in_old and in_new:
                result.append(self._format_output(f"  {item_str},", "append"))
                have_changes = True
            else:
                result.append(self._format_output(f"  {item_str},", "no_diff"))

        if not have_changes:
            return []

        # Убираем лишнюю запятую у последнего элемента:
        head, sep, tail = result[-1].rpartition(',')
        result[-1] = head + tail

        return result


    def _format_differences(
        self, differences: List[Tuple[List[str], Any, Any]]
    ) -> str:
        """Форматирует найденные различия в читаемый вид."""
        output: List[str] = []
        for path, old_val, new_val in differences:
            p = self._format_path(path)
            # Списки
            if isinstance(old_val, list) and isinstance(new_val, list):
                output.extend(self._format_list_diff(p, old_val, new_val))
            # Добавление
            elif old_val is None:
                if isinstance(new_val, list):
                    output.extend(self._format_list_diff(p, None, new_val))
                else:
                    output.append(self._format_output(f"{p}: {json.dumps(new_val, ensure_ascii=False)}", "append"))
            # Удаление
            elif new_val is None:
                if isinstance(old_val, list):
                    output.extend(self._format_list_diff(p, old_val, None))
                else:
                    output.append(self._format_output(f"{p}: {json.dumps(old_val, ensure_ascii=False)}", "remove"))
            # Замена простого значения
            elif not isinstance(old_val, (dict, list)) and not isinstance(new_val, (dict, list)):
                output.append(self._format_output(f"{p}: {json.dumps(old_val)} -> {json.dumps(new_val)}", "replace"))
            # Сложные структуры
            else:
                old_json = json.dumps(old_val, indent=2, ensure_ascii=False)
                new_json = json.dumps(new_val, indent=2, ensure_ascii=False)
                output.append(self._format_output(f"{p}:", "replace"))
                for line in old_json.splitlines():
                    output.append(self._format_output(f"  {line}", "remove"))
                
                for line in new_json.splitlines():
                    output.append(self._format_output(f"  {line}", "append"))

            if len(output) == 0 or len(output[-1]) != 0: output.append("")
        return "\n".join(output).rstrip()
