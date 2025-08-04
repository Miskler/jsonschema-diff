from typing import Any
from .abstraction import Statuses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Config

class Compare:
    def __init__(self,
                 config: "Config",
                 json_path: list[str],
                 old_key: str | None,
                 old_value: Any,
                 new_key: str | None,
                 new_value: Any):
        self.status = Statuses.UNKNOWN

        self.config = config
        self.json_path = json_path

        self.old_key = old_key
        self.old_value = old_value
        self.new_key = new_key
        self.new_value = new_value

    def compare(self) -> Statuses:
        if self.old_key is None and self.new_key is not None: # add
            self.status = Statuses.ADDED
        elif self.old_key is not None and self.new_key is None: # remove
            self.status = Statuses.DELETED
        elif self.old_key is not None and self.new_key is not None: # replace or no-diff
            if str(self.new_value) == str(self.old_value):
                self.status = Statuses.NO_DIFF
            else:
                self.status = Statuses.REPLACED
        else:
            raise ValueError

        return self.status

    def is_for_rendering(self) -> bool:
        return self.status in [Statuses.ADDED, Statuses.DELETED, Statuses.REPLACED, Statuses.MODIFIED]

    def _render_start_line(self, tab_level: int = 0, with_path: bool = True, with_key: bool = True) -> str:
        to_return = f"{self.status.value} {self.config.TAB * tab_level}"
        if with_path:
            to_join = []
            for x in self.json_path:
                if x.isnumeric():
                    to_join.append(f'[{x}]')
                else:
                    to_join.append(f'["{x}"]')
            
            to_return += ''.join(to_join)
        if with_key:
            to_return += f".{self.new_key}"
        return to_return+":"

    def render(self, tab_level: int = 0) -> str:
        to_return = self._render_start_line(tab_level)

        if self.status in [Statuses.ADDED, Statuses.DELETED, Statuses.NO_DIFF]:
            to_return += f" {self.new_value}"
        elif self.status == Statuses.REPLACED:
            to_return += f" {self.old_value} -> {self.new_value}"
        
        return to_return
