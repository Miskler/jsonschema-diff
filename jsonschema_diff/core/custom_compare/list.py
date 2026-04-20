import hashlib
import json
import string
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from ..abstraction import Statuses
from ..compare_base import Compare
from ..property import Property

if TYPE_CHECKING:
    from ..compare_base import LEGEND_RETURN_TYPE
    from ..config import Config


@dataclass
class CompareListElement:
    config: "Config"
    my_config: dict
    value: Any
    status: Statuses
    compared_property: Optional[Property] = None

    def compare(self) -> None:
        # Если элемент списка — словарь, рендерим его как Property
        if isinstance(self.value, dict):
            # Подбираем old/new под статус элемента
            if self.status == Statuses.DELETED:
                old_schema = self.value
                new_schema = None
            elif self.status == Statuses.ADDED:
                old_schema = None
                new_schema = self.value
            else:
                # NO_DIFF и прочие — считаем, что значение одинаково слева и справа
                old_schema = self.value
                new_schema = self.value

            self.compared_property = Property(
                config=self.config,
                name=None,
                schema_path=[],
                json_path=[],
                old_schema=old_schema,
                new_schema=new_schema,
            )
            self.compared_property.compare()

    def replace_penultimate_space(self, tab_level: int, s: str, repl: str) -> str:
        position = (
            len(self.config.TAB) * tab_level
        )  # 1 + (len(self.config.TAB) * tab_level) - 1 # PREFIX + TAB * COUNT - 1
        return s[:position] + repl + s[position:]

    def _probe_tail(self, line: str, tab_level: int) -> str:
        return line[len(self.config.TAB) * tab_level :].lstrip()

    def _probe(self, line: str, tab_level: int) -> str:
        return line[len(self.config.TAB) * tab_level :]

    @staticmethod
    def _is_header_tail(tail: str) -> bool:
        return tail.endswith(":")

    @staticmethod
    def _is_bullet_tail(tail: str) -> bool:
        return tail.startswith("•")

    @staticmethod
    def _leading_spaces(value: str) -> int:
        return len(value) - len(value.lstrip(" "))

    def _raw_pairs(self, tab_level: int = 0) -> list[tuple[Statuses, str]]:
        if self.compared_property is not None:
            render_lines, _render_compares = self.compared_property._render_pairs(
                tab_level=tab_level
            )
            return render_lines

        # Иначе — старое поведение (строка/число/пр. выводим как есть)
        return [(self.status, f"{self.status.value} {self.config.TAB * tab_level}{self.value}")]

    def _is_nested_scalar_list(
        self, lines: list[tuple[Statuses, str]], tab_level: int
    ) -> bool:
        if self.compared_property is None or len(lines) <= 1:
            return False

        first_line = lines[0][1]
        if ":" not in first_line:
            return False

        markers = {
            value
            for value in (
                self.my_config.get("SINGLE_LINE", " "),
                self.my_config.get("START_LINE", " "),
                self.my_config.get("MIDDLE_LINE", " "),
                self.my_config.get("END_LINE", " "),
            )
            if value != " "
        }
        if len(markers) <= 0:
            return False

        probe_start = len(self.config.TAB) * tab_level
        for _status, line in lines[1:]:
            probe = line[probe_start:]
            marker_positions = [
                (probe.find(marker), marker) for marker in markers if probe.find(marker) != -1
            ]
            if len(marker_positions) <= 0:
                return False
            marker_idx, marker = min(marker_positions, key=lambda item: item[0])
            tail = probe[marker_idx + len(marker) :].strip()
            if len(tail) <= 0:
                return False
            if tail.endswith(":"):
                return False
            if tail.startswith(".") or tail.startswith("["):
                return False

        return True

    def _render_nested_scalar_list(
        self, lines: list[tuple[Statuses, str]], tab_level: int
    ) -> list[tuple[Statuses, str]]:
        head_status, head_line = lines[0]
        rendered = [
            (
                head_status,
                self.replace_penultimate_space(
                    tab_level=tab_level,
                    s=head_line,
                    repl=self.my_config.get("SINGLE_LINE", " "),
                ),
            )
        ]

        body = lines[1:]
        if len(body) == 1:
            only_status, only_line = body[0]
            rendered.append(
                (
                    only_status,
                    self.replace_penultimate_space(
                        tab_level=tab_level,
                        s=only_line,
                        repl=self.my_config.get("SINGLE_LINE", " "),
                    ),
                )
            )
            return rendered

        for idx, (line_status, line) in enumerate(body):
            if idx == 0:
                repl = self.my_config.get("START_LINE", " ")
            elif idx == len(body) - 1:
                repl = self.my_config.get("END_LINE", " ")
            else:
                repl = self.my_config.get("MIDDLE_LINE", " ")

            rendered.append(
                (
                    line_status,
                    self.replace_penultimate_space(tab_level=tab_level, s=line, repl=repl),
                )
            )

        return rendered

    def _render_group(
        self, group: list[tuple[Statuses, str]], tab_level: int
    ) -> list[tuple[Statuses, str]]:
        if len(group) <= 0:
            return []

        if len(group) == 1:
            return [
                (
                    group[0][0],
                    self.replace_penultimate_space(
                        tab_level=tab_level,
                        s=group[0][1],
                        repl=self.my_config.get("SINGLE_LINE", " "),
                    ),
                )
            ]

        rendered: list[tuple[Statuses, str]] = []
        for idx, (line_status, line) in enumerate(group):
            if idx == 0:
                repl = self.my_config.get("START_LINE", " ")
            elif idx == len(group) - 1:
                repl = self.my_config.get("END_LINE", " ")
            else:
                repl = self.my_config.get("MIDDLE_LINE", " ")

            rendered.append(
                (
                    line_status,
                    self.replace_penultimate_space(tab_level=tab_level, s=line, repl=repl),
                )
            )

        return rendered

    def _split_logical_groups(
        self, lines: list[tuple[Statuses, str]], tab_level: int
    ) -> list[list[tuple[Statuses, str]]]:
        groups: list[list[tuple[Statuses, str]]] = []
        i = 0

        while i < len(lines):
            current_probe = self._probe(lines[i][1], tab_level)
            current_indent = self._leading_spaces(current_probe)
            current_tail = current_probe.lstrip()

            # Preserve "header + its bullet/deeper children" as a single block,
            # even if statuses differ inside that block.
            if self._is_header_tail(current_tail):
                j = i + 1
                while j < len(lines):
                    next_probe = self._probe(lines[j][1], tab_level)
                    next_indent = self._leading_spaces(next_probe)
                    next_tail = next_probe.lstrip()

                    if next_indent < current_indent:
                        break
                    if next_indent == current_indent and not self._is_bullet_tail(next_tail):
                        break
                    j += 1

                if j > i + 1:
                    groups.append(lines[i:j])
                    i = j
                    continue

            status = lines[i][0]
            j = i + 1
            while j < len(lines) and lines[j][0] == status:
                j += 1

            groups.append(lines[i:j])
            i = j

        return groups

    def _render_pairs(self, tab_level: int = 0) -> list[tuple[Statuses, str]]:
        lines = [
            (status, line)
            for status, line in self._raw_pairs(tab_level=tab_level)
            if line.strip() != ""
        ]
        if len(lines) <= 0:
            # В крайне редких случаях, длина списка == 0
            # мне лень разбираться, так что легализуем
            return []

        if self._is_nested_scalar_list(lines, tab_level):
            return self._render_nested_scalar_list(lines, tab_level)

        to_return: list[tuple[Statuses, str]] = []
        for group in self._split_logical_groups(lines, tab_level):
            to_return.extend(self._render_group(group, tab_level))

        return to_return

    def render(self, tab_level: int = 0) -> Optional[str]:
        lines_with_status = self._render_pairs(tab_level=tab_level)
        if len(lines_with_status) <= 0:
            return None
        return "\n".join([line for _status, line in lines_with_status])


class CompareList(Compare):
    DELETED_LIST_RENDER_DEFAULT = "[{count} items]"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.elements: list[CompareListElement] = []
        self.changed_elements: list[CompareListElement] = []

    def _deleted_list_render_template(self) -> str | None:
        template = self.my_config.get("DELETED_LIST_RENDER", self.DELETED_LIST_RENDER_DEFAULT)
        if template is None:
            return None
        if not isinstance(template, str):
            raise TypeError("CompareList DELETED_LIST_RENDER must be str or None")

        formatter = string.Formatter()
        field_names = {
            field_name
            for _literal_text, field_name, _format_spec, _conversion in formatter.parse(template)
            if field_name is not None
        }
        if "count" not in field_names:
            raise ValueError("CompareList DELETED_LIST_RENDER must contain {count}")

        return template

    def _deleted_items_count(self) -> int:
        if isinstance(self.old_value, list):
            return len(self.old_value)
        if self.old_value is None:
            return 0
        return 1

    def _render_deleted_summary(
        self, tab_level: int = 0, with_path: bool = True, to_crop: tuple[int, int] = (0, 0)
    ) -> list[tuple[Statuses, str]] | None:
        if self.status is not Statuses.DELETED:
            return None

        template = self._deleted_list_render_template()
        if template is None:
            return None

        return [
            (
                self.status,
                f"{self._render_start_line(tab_level=tab_level, with_path=with_path, to_crop=to_crop)} "
                f"{template.format(count=self._deleted_items_count())}",
            )
        ]

    # --- вспомогательное: score ∈ [0..1] из Property.calc_diff()
    def _score_from_stats(self, stats: Dict[str, int]) -> float:
        unchanged = stats.get("NO_DIFF", 0) + stats.get("UNKNOWN", 0)
        changed = (
            stats.get("ADDED", 0) + stats.get("DELETED", 0) + stats.get("REPLACED", 0)
        )  # модификации не в счет + stats.get("MODIFIED", 0)
        denom = unchanged + changed
        if denom == 0:
            return 1.0
        return unchanged / float(denom)

    @staticmethod
    def _stable_repr(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        except TypeError:
            return str(value)

    @staticmethod
    def _scalar_match_key(value: Any) -> str:
        return f"{type(value).__qualname__}:{CompareList._stable_repr(value)}"

    @staticmethod
    def _stable_tie_break(old_repr: str, new_repr: str) -> float:
        digest = hashlib.sha1(f"{old_repr}|{new_repr}".encode("utf-8")).digest()
        return (int.from_bytes(digest[:8], byteorder="big", signed=False) / (2**64)) * 1e-9

    @staticmethod
    def _hungarian_max(weights: list[list[float]]) -> list[int]:
        row_count = len(weights)
        if row_count == 0:
            return []

        column_count = len(weights[0])
        if column_count < row_count:
            raise ValueError("Hungarian solver expects columns >= rows")

        max_weight = max(max(row) for row in weights)
        cost = [[max_weight - w for w in row] for row in weights]

        u = [0.0] * (row_count + 1)
        v = [0.0] * (column_count + 1)
        p = [0] * (column_count + 1)
        way = [0] * (column_count + 1)

        for i in range(1, row_count + 1):
            p[0] = i
            j0 = 0
            minv = [float("inf")] * (column_count + 1)
            used = [False] * (column_count + 1)

            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float("inf")
                j1 = 0

                for j in range(1, column_count + 1):
                    if used[j]:
                        continue
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

                for j in range(column_count + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta

                j0 = j1
                if p[j0] == 0:
                    break

            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1
                if j0 == 0:
                    break

        assignment = [-1] * row_count
        for j in range(1, column_count + 1):
            if p[j] != 0:
                assignment[p[j] - 1] = j - 1

        return assignment

    def compare(self) -> Statuses:
        super().compare()

        if self.status == Statuses.NO_DIFF:
            return self.status
        elif self.status in [Statuses.ADDED, Statuses.DELETED]:  # add
            for v in self.value:
                element = CompareListElement(self.config, self.my_config, v, self.status)
                element.compare()
                self.elements.append(element)
                self.changed_elements.append(element)
        elif self.status == Statuses.REPLACED:  # replace or no-diff
            # ------------------------------
            # 1) Матричное сопоставление dict↔dict (order-independent)
            # ------------------------------
            old_list = self.old_value if isinstance(self.old_value, list) else [self.old_value]
            new_list = self.new_value if isinstance(self.new_value, list) else [self.new_value]

            old_dicts: list[tuple[int, dict]] = [
                (i, v) for i, v in enumerate(old_list) if isinstance(v, dict)
            ]
            new_dicts: list[tuple[int, dict]] = [
                (j, v) for j, v in enumerate(new_list) if isinstance(v, dict)
            ]

            threshold = float(self.my_config.get("DICT_MATCH_THRESHOLD", 0.10))

            matched_old: set[int] = set()
            matched_new: set[int] = set()

            if len(old_dicts) > 0 and len(new_dicts) > 0:
                row_count = len(old_dicts)
                real_column_count = len(new_dicts)

                old_repr = [self._stable_repr(item[1]) for item in old_dicts]
                new_repr = [self._stable_repr(item[1]) for item in new_dicts]

                # Добавляем "dummy" колонки (unmatched old), чтобы не форсировать плохие пары.
                score_matrix: list[list[float]] = [
                    [0.0 for _ in range(real_column_count + row_count)] for _ in range(row_count)
                ]
                properties: dict[tuple[int, int], tuple[float, Property]] = {}

                disallowed_score = -1_000_000.0
                for old_row, (_oi, ov) in enumerate(old_dicts):
                    for new_col, (_nj, nv) in enumerate(new_dicts):
                        prop = Property(
                            config=self.config,
                            name=None,
                            schema_path=[],
                            json_path=[],
                            old_schema=ov,
                            new_schema=nv,
                        )
                        prop.compare()
                        score = self._score_from_stats(prop.calc_diff())
                        properties[(old_row, new_col)] = (score, prop)

                        if score >= threshold:
                            score_matrix[old_row][new_col] = score + self._stable_tie_break(
                                old_repr[old_row],
                                new_repr[new_col],
                            )
                        else:
                            score_matrix[old_row][new_col] = disallowed_score

                assignment = self._hungarian_max(score_matrix)
                matched_by_old_row: dict[int, tuple[int, Property]] = {}

                for old_row, matched_col in enumerate(assignment):
                    if matched_col < 0 or matched_col >= real_column_count:
                        continue

                    score, prop = properties[(old_row, matched_col)]
                    if score >= threshold:
                        matched_by_old_row[old_row] = (matched_col, prop)

                for old_row, (oi, _ov) in enumerate(old_dicts):
                    pair = matched_by_old_row.get(old_row)
                    if pair is None:
                        continue

                    matched_col, prop = pair
                    nj, _nv = new_dicts[matched_col]

                    matched_old.add(oi)
                    matched_new.add(nj)

                    # добавляем как один элемент списка с compared_property
                    # статус NO_DIFF, если проперти без отличий, иначе MODIFIED
                    status = (
                        Statuses.NO_DIFF if prop.status == Statuses.NO_DIFF else Statuses.MODIFIED
                    )
                    el = CompareListElement(
                        self.config,
                        self.my_config,
                        value=None,
                        status=status,
                        compared_property=prop,
                    )
                    self.elements.append(el)
                    if status != Statuses.NO_DIFF:
                        self.changed_elements.append(el)

            # все старые dict, что не подобрались → DELETED
            for oi, ov in old_dicts:
                if oi not in matched_old:
                    el = CompareListElement(
                        self.config, self.my_config, value=ov, status=Statuses.DELETED
                    )
                    el.compare()
                    self.elements.append(el)
                    self.changed_elements.append(el)

            # все новые dict, что не подобрались → ADDED
            for nj, nv in new_dicts:
                if nj not in matched_new:
                    el = CompareListElement(
                        self.config, self.my_config, value=nv, status=Statuses.ADDED
                    )
                    el.compare()
                    self.elements.append(el)
                    self.changed_elements.append(el)

            # ------------------------------
            # 2) НЕ-словари: order-insensitive multiset diff
            #    ВАЖНО: словари из сравнения исключаем, чтобы не дублировать их как insert/delete
            # ------------------------------
            def filter_non_dict(src: list[Any]) -> list[Any]:
                return [v for v in src if not isinstance(v, dict)]

            old_rest = filter_non_dict(old_list)
            new_rest = filter_non_dict(new_list)

            old_pool: dict[str, deque[int]] = defaultdict(deque)
            for old_idx, old_value in enumerate(old_rest):
                old_pool[self._scalar_match_key(old_value)].append(old_idx)

            matched_old_indices: set[int] = set()

            def add_element(value: Any, status: Statuses) -> None:
                element = CompareListElement(self.config, self.my_config, value, status)
                element.compare()
                self.elements.append(element)
                if status != Statuses.NO_DIFF:
                    self.changed_elements.append(element)

            # Рендерим в порядке new: совпавшие элементы считаем NO_DIFF, "лишние" справа — ADDED.
            for new_value in new_rest:
                key = self._scalar_match_key(new_value)
                bucket = old_pool.get(key)
                if bucket is not None and len(bucket) > 0:
                    old_idx = bucket.popleft()
                    matched_old_indices.add(old_idx)
                    add_element(old_rest[old_idx], Statuses.NO_DIFF)
                else:
                    add_element(new_value, Statuses.ADDED)

            # Все непокрытые элементы old — DELETED (в старом порядке).
            for old_idx, old_value in enumerate(old_rest):
                if old_idx not in matched_old_indices:
                    add_element(old_value, Statuses.DELETED)

            if len(self.changed_elements) > 0:
                self.status = Statuses.MODIFIED
            else:
                self.status = Statuses.NO_DIFF
        else:
            raise ValueError("Unsupported keys combination")

        return self.status

    def is_for_rendering(self) -> bool:
        return super().is_for_rendering() or len(self.changed_elements) > 0

    def render(
        self, tab_level: int = 0, with_path: bool = True, to_crop: tuple[int, int] = (0, 0)
    ) -> str:
        lines = self._render_pairs(tab_level=tab_level, with_path=with_path, to_crop=to_crop)
        return "\n".join([line for _status, line in lines])

    def _render_pairs(
        self, tab_level: int = 0, with_path: bool = True, to_crop: tuple[int, int] = (0, 0)
    ) -> list[tuple[Statuses, str]]:
        deleted_summary = self._render_deleted_summary(
            tab_level=tab_level, with_path=with_path, to_crop=to_crop
        )
        if deleted_summary is not None:
            return deleted_summary

        to_return: list[tuple[Statuses, str]] = [
            (
                self.status,
                self._render_start_line(tab_level=tab_level, with_path=with_path, to_crop=to_crop),
            )
        ]

        for i in self.elements:
            to_return += i._render_pairs(tab_level + 1)
        return to_return

    @staticmethod
    def legend() -> "LEGEND_RETURN_TYPE":
        return {
            "element": "Arrays\nLists",
            "description": (
                "Arrays are always displayed fully, with statuses of all elements "
                "separately (left to them).\nIn example:\n"
                '["Masha", "Misha", "Vasya"] replace to ["Masha", "Olya", "Misha"]'
            ),
            "example": {
                "old_value": {"some_list": ["Masha", "Misha", "Vasya"]},
                "new_value": {"some_list": ["Masha", "Olya", "Misha"]},
            },
        }
