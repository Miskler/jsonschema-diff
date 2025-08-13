from typing import Any
from ..abstraction import Statuses
from ..parameter_base import Compare
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
import difflib

if TYPE_CHECKING:
    from ..config import Config


@dataclass
class CompareListElement:
    config: "Config"
    value: Any
    status: Statuses
    
    def render(self, tab_level: int = 0) -> str:
        return f"{self.status.value} {self.config.TAB * tab_level}{self.value}"


class CompareList(Compare):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elements: list[CompareListElement] = []
        self.changed_elements: list[CompareListElement] = []

    def compare(self) -> Statuses:
        super().compare()

        if self.status == Statuses.NO_DIFF:
            return self.status
        elif self.status in [Statuses.ADDED, Statuses.DELETED]: # add
            for v in self.value:
                element = CompareListElement(self.config, v, self.status)
                self.elements.append(element)
                self.changed_elements.append(element)
        elif self.status == Statuses.REPLACED: # replace or no-diff
            sm = difflib.SequenceMatcher(a=self.old_value, b=self.new_value, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                def add_element(status: Statuses, from_index: int, to_index: int):
                    is_change = status != Statuses.NO_DIFF
                    for v in self.old_value[from_index:to_index]:
                        element = CompareListElement(self.config, v, status)
                        self.elements.append(element)
                        if is_change:
                            self.changed_elements.append(element)

                match tag:
                    case "equal":
                        add_element(Statuses.NO_DIFF, i1, i2)
                    case "delete":
                        add_element(Statuses.DELETED, i1, i2)
                    case "insert":
                        add_element(Statuses.ADDED, j1, j2)
                    case "replace":
                        add_element(Statuses.DELETED, i1, i2)
                        add_element(Statuses.ADDED, j1, j2)
                    case _:
                        ValueError(f"Unknown tag: {tag}")
            
            if len(self.changed_elements) > 0:
                self.status = Statuses.MODIFIED
            else:
                self.status = Statuses.NO_DIFF
        else:
            raise ValueError(f"Unsupported keys combination")

        return self.status
    
    def is_for_rendering(self) -> bool:
        return super().is_for_rendering() or len(self.changed_elements) > 0
    
    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        to_return = self._render_start_line(tab_level=tab_level, with_path=with_path)
        
        for i in self.elements:
            to_return += f"\n{i.render(tab_level + 1)}"
        return to_return


    @staticmethod
    def legend() -> dict[str, Any]:
        return {
            "element": "Arrays / Lists",
            "description": "Arrays are always displayed fully, with statuses of all elements separately (left to them).\nIn example: [1, 2, 3] replace to [4, 1, 2]",
            "example": {
                "old_value": {"some_list": ["11", "22", "33"]},
                "new_value": {"some_list": ["44", "11", "22"]}
            }
        }
