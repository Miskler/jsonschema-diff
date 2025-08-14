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

        return self.status

    def get_name(self) -> str:
        raise NotImplementedError("CompareCombined.get_name должен быть переопределен")

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        raise NotImplementedError("CompareCombined.render должен быть переопределен")

    @staticmethod
    def legend() -> dict[str, str | list[str]]:
        raise NotImplementedError("CompareCombined.legend должен быть переопределен")
