from typing import Any
from .abstraction import Statuses
from jsonschema_diff.compare.parameter_base import Compare
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
        if self.old_key is None and self.new_key is not None: # add
            self.status = Statuses.ADDED

            for new_value in self.new_value:
                element = CompareListElement(self.config, new_value, Statuses.ADDED)
                self.elements.append(element)
                self.changed_elements.append(element)
        elif self.old_key is not None and self.new_key is None: # remove
            self.status = Statuses.DELETED

            for old_value in self.old_value:
                element = CompareListElement(self.config, old_value, Statuses.DELETED)
                self.elements.append(element)
                self.changed_elements.append(element)
        elif self.old_key is not None and self.new_key is not None: # replace or no-diff
            sm = difflib.SequenceMatcher(a=self.old_value, b=self.new_value, autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                match tag:
                    case "equal":
                        for v in self.old_value[i1:i2]:
                            element = CompareListElement(self.config, v, Statuses.NO_DIFF)
                            self.elements.append(element)
                    case "delete":
                        for v in self.old_value[i1:i2]:
                            element = CompareListElement(self.config, v, Statuses.DELETED)
                            self.elements.append(element)
                            self.changed_elements.append(element)
                    case "insert":
                        for v in self.new_value[j1:j2]:
                            element = CompareListElement(self.config, v, Statuses.ADDED)
                            self.elements.append(element)
                            self.changed_elements.append(element)
                    case "replace":
                        for v in self.old_value[i1:i2]:
                            element = CompareListElement(self.config, v, Statuses.DELETED)
                            self.elements.append(element)
                            self.changed_elements.append(element)
                        for v in self.new_value[j1:j2]:
                            element = CompareListElement(self.config, v, Statuses.ADDED)
                            self.elements.append(element)
                            self.changed_elements.append(element)
                    case _:
                        ValueError(f"Unknown tag: {tag}")
            
            self.status = Statuses.MODIFIED if len(self.changed_elements) > 0 else Statuses.NO_DIFF
        else:
            raise ValueError(f"Unsupported keys combination")

        return self.status
    
    def is_for_rendering(self) -> bool:
        return super().is_for_rendering() or len(self.changed_elements) > 0
    
    def render(self, tab_level: int = 0) -> str:
        to_return = self._render_start_line(tab_level)
        for i in self.elements:
            to_return += f"\n{i.render(tab_level + 1)}"
        return to_return
