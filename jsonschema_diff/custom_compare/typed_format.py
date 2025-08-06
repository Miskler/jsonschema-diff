from typing import Any
from ..abstraction import Statuses
from ..parameter_base import Compare


class CompareTypedFormat(Compare):
    def compare(self) -> Statuses:
        print(f"{len(self.to_compare)} {', '.join(str(k.key) for k in self.to_compare)}")
        return Statuses.NO_DIFF

    def is_for_rendering(self) -> bool:
        return False
