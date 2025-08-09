
from .abstraction import Statuses
from .parameter_base import Compare


class CompareCombined(Compare):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dict_compare = {}
        self.dict_values = {}

    def compare(self) -> Statuses:
        for c in self.to_compare:
            if self.status == Statuses.UNKNOWN:
                self.status = c.status
            elif self.status != c.status:
                self.status = Statuses.REPLACED

            self.dict_compare[c.key] = c
            self.dict_values[c.key] = c.value
        
        from pprint import pprint
        print(self.dict_compare, flush=True)

        return self.status

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        raise NotImplementedError("CompareCombined.render должен быть переопределен")
