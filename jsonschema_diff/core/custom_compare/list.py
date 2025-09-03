import difflib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

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

    def _real_render(self, tab_level: int = 0) -> str:
        if self.compared_property is not None:
            render_lines, _render_compares = self.compared_property.render(
                tab_level=tab_level, all_for_rendering=True
            )

            return "\n".join(render_lines)

        # Иначе — старое поведение (строка/число/пр. выводим как есть)
        return f"{self.status.value} {self.config.TAB * tab_level}{self.value}"

    def render(self, tab_level: int = 0) -> str:
        lines = [
            line
            for line in self._real_render(tab_level=tab_level).split("\n")
            if line.strip() != ""
        ]
        # первая строка = START_LINE, последняя = END_LINE, остальное = MIDDLE_LINE
        if len(lines) > 1:
            prepare = []
            for i, line in enumerate(lines):
                if i == 0:
                    prepare.append(
                        self.replace_penultimate_space(
                            tab_level=tab_level, s=line, repl=self.my_config.get("START_LINE", " ")
                        )
                    )
                elif i == len(lines) - 1:
                    prepare.append(
                        self.replace_penultimate_space(
                            tab_level=tab_level, s=line, repl=self.my_config.get("END_LINE", " ")
                        )
                    )
                else:
                    prepare.append(
                        self.replace_penultimate_space(
                            tab_level=tab_level, s=line, repl=self.my_config.get("MIDDLE_LINE", " ")
                        )
                    )

            return "\n".join(prepare)
        else:
            return self.replace_penultimate_space(
                tab_level=tab_level, s=lines[0], repl=self.my_config.get("SINGLE_LINE", " ")
            )


class CompareList(Compare):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.elements: list[CompareListElement] = []
        self.changed_elements: list[CompareListElement] = []

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
            # делаем гарантированно массив строк прогоняя циклом
            def get_str_list(v: Any) -> list[str] | str:
                if isinstance(v, list):
                    return [str(i) for i in v]
                return str(v)

            real_old_value = get_str_list(self.old_value)
            real_new_value = get_str_list(self.new_value)

            sm = difflib.SequenceMatcher(a=real_old_value, b=real_new_value, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():

                def add_element(
                    source: list[Any], status: Statuses, from_index: int, to_index: int
                ) -> None:
                    is_change = status != Statuses.NO_DIFF
                    for v in source[from_index:to_index]:
                        element = CompareListElement(self.config, self.my_config, v, status)
                        element.compare()
                        self.elements.append(element)
                        if is_change:
                            self.changed_elements.append(element)

                match tag:
                    case "equal":
                        add_element(self.old_value, Statuses.NO_DIFF, i1, i2)
                    case "delete":
                        add_element(self.old_value, Statuses.DELETED, i1, i2)
                    case "insert":
                        add_element(self.new_value, Statuses.ADDED, j1, j2)
                    case "replace":
                        add_element(self.old_value, Statuses.DELETED, i1, i2)
                        add_element(self.new_value, Statuses.ADDED, j1, j2)
                    case _:
                        raise ValueError(f"Unknown tag: {tag}")

            if len(self.changed_elements) > 0:
                self.status = Statuses.MODIFIED
            else:
                self.status = Statuses.NO_DIFF
        else:
            raise ValueError("Unsupported keys combination")

        return self.status

    def is_for_rendering(self) -> bool:
        return super().is_for_rendering() or len(self.changed_elements) > 0

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        to_return = self._render_start_line(tab_level=tab_level, with_path=with_path)

        for i in self.elements:
            to_return += f"\n{i.render(tab_level + 1)}"
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
