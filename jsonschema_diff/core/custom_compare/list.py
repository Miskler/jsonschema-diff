import difflib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..abstraction import Statuses
from ..compare_base import Compare

if TYPE_CHECKING:
    from ..compare_base import LEGEND_RETURN_TYPE
    from ..config import Config


@dataclass
class CompareListElement:
    config: "Config"
    value: Any
    status: Statuses

    def render(self, tab_level: int = 0) -> str:
        return f"{self.status.value} {self.config.TAB * tab_level}{self.value}"


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
                element = CompareListElement(self.config, v, self.status)
                self.elements.append(element)
                self.changed_elements.append(element)
        elif self.status == Statuses.REPLACED:  # replace or no-diff
            # делаем гарантированно массив строк прогоняя циклом
            real_old_value = [str(v) for v in self.old_value]
            real_new_value = [str(v) for v in self.new_value]

            sm = difflib.SequenceMatcher(a=real_old_value, b=real_new_value, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():

                def add_element(
                    source: list[Any], status: Statuses, from_index: int, to_index: int
                ) -> None:
                    is_change = status != Statuses.NO_DIFF
                    for v in source[from_index:to_index]:
                        element = CompareListElement(self.config, v, status)
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
