from typing import Any
from types import NoneType
from typing import TYPE_CHECKING

from .parameter_base import Compare
from .parameter_list import CompareList

class CompareRules:
    def __init__(self, rules: dict[type | tuple[type, type], type[Compare]] = {}, default: type[Compare] = Compare):
        self.compare_rules = rules
        self.default = default
    
    def get_comparator_from_values(self, old: Any, new: Any) -> type[Compare]:
        return self.get_comparator(type(old), type(new))

    def get_comparator(self, old: type, new: type) -> type[Compare]:
        if new is NoneType and old is NoneType:
            raise ValueError("Cannot compare None to None")
        
        tuple_types = self.compare_rules.get((old, new), None)
        if tuple_types is not None:
            return tuple_types
        else:
            if old is NoneType:
                return self.compare_rules.get(new, self.default)
            elif old is not NoneType or old is new:
                return self.compare_rules.get(old, self.default)


class Config:
    def __init__(self,
                 tab: str = "  ",
                 compare_rules: CompareRules | None = None,
                 path_maker_ignore: list[str] = ["properties", "items"]):
        self.TAB = tab
        if compare_rules is None:
            self.COMPARE_RULES = CompareRules()
        self.COMPARE_RULES = compare_rules
        self.PATH_MAKER_IGNORE = path_maker_ignore


config = Config(compare_rules=CompareRules({list: CompareList}))
