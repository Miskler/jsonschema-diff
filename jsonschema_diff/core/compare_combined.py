from typing import TYPE_CHECKING, Any, Dict

from .abstraction import Statuses, ToCompare
from .compare_base import Compare

if TYPE_CHECKING:
    from .compare_base import LEGEND_RETURN_TYPE


class CompareCombined(Compare):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.dict_compare: Dict[str, ToCompare] = {}
        self.dict_values: Dict[str, Any] = {}

    def compare(self) -> Statuses:
        for c in self.to_compare:
            if self.status == Statuses.UNKNOWN:
                self.status = c.status
            elif self.status != c.status:
                self.status = Statuses.REPLACED

            self.dict_compare[c.key] = c
            self.dict_values[c.key] = c.value

        return self.status

    def calc_diff(self) -> dict[str, int]:
        """
        Multiple implementation: counts its own status as the number of keys.
        Complex comparators (e.g. CompareList) override this to return an aggregate.
        """
        stats = {self.status.name: 1}
        for comp in self.dict_compare.values():
            if comp.status.name not in stats:
                stats[comp.status.name] = 0
            stats[comp.status.name] += 1

        return stats

    def get_name(self) -> str:
        raise NotImplementedError("The get_name method must be overridden")

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        raise NotImplementedError("The render method must be overridden")

    @staticmethod
    def legend() -> "LEGEND_RETURN_TYPE":
        raise NotImplementedError("The legend method must be overridden")
