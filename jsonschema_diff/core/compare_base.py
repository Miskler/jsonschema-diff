from typing import TYPE_CHECKING, Any, TypeAlias

from .abstraction import Statuses, ToCompare
from .tools.render import RenderTool

if TYPE_CHECKING:
    from .config import Config

COMPARE_PATH_TYPE: TypeAlias = list[str | int]
LEGEND_PROCESSOR_TYPE: TypeAlias = dict[str, Any]
LEGEND_RETURN_TYPE: TypeAlias = dict[
    str, str | LEGEND_PROCESSOR_TYPE | list[str | LEGEND_PROCESSOR_TYPE]
]


class Compare:
    def __init__(
        self,
        config: "Config",
        schema_path: COMPARE_PATH_TYPE,
        json_path: COMPARE_PATH_TYPE,
        to_compare: list[ToCompare],
    ):
        self.status = Statuses.UNKNOWN

        self.config = config
        self.schema_path = schema_path
        self.json_path = json_path

        if len(to_compare) <= 0:
            raise ValueError("Cannot compare empty list")
        self.to_compare = to_compare

    @property
    def my_config(self) -> dict:
        return self.config.COMPARE_CONFIG.get(type(self), {})

    def compare(self) -> Statuses:
        if len(self.to_compare) > 1:
            raise ValueError("Unsupported multiple compare for base logic")

        self.status = self.to_compare[0].status
        self.key = self.to_compare[0].key
        self.value = self.to_compare[0].value
        self.old_value = self.to_compare[0].old_value
        self.new_value = self.to_compare[0].new_value
        return self.status

    def get_name(self) -> str:
        return self.to_compare[0].key

    def is_for_rendering(self) -> bool:
        return self.status in [
            Statuses.ADDED,
            Statuses.DELETED,
            Statuses.REPLACED,
            Statuses.MODIFIED,
        ]

    def calc_diff(self) -> dict[str, int]:
        """
        Basic implementation: counts its own status as 1 element.
        Complex comparators (e.g. CompareList) override this to return an aggregate.
        """
        return {self.status.name: 1}

    def _render_start_line(
        self, tab_level: int = 0, with_path: bool = True, with_key: bool = True
    ) -> str:
        to_return = (
            f"{RenderTool.make_prefix(self.status)} {RenderTool.make_tab(self.config, tab_level)}"
        )
        if with_path:
            to_return += RenderTool.make_path(
                self.schema_path, self.json_path, ignore=self.config.PATH_MAKER_IGNORE
            )

        if with_key:
            to_return += f".{self.get_name()}"
        return to_return + ":"

    def render(self, tab_level: int = 0, with_path: bool = True) -> str:
        to_return = self._render_start_line(tab_level=tab_level, with_path=with_path)

        if self.status in [Statuses.ADDED, Statuses.DELETED, Statuses.NO_DIFF]:
            to_return += f" {self.value}"
        elif self.status == Statuses.REPLACED:
            to_return += f" {self.old_value} -> {self.new_value}"
        else:
            raise ValueError(f"Unsupported for render status: {self.status}")

        return to_return

    @staticmethod
    def legend() -> LEGEND_RETURN_TYPE:
        return {
            "element": [
                Statuses.ADDED.value,
                Statuses.DELETED.value,
                Statuses.REPLACED.value,
                Statuses.MODIFIED.value,
                Statuses.NO_DIFF.value,
                Statuses.UNKNOWN.value,
            ],
            "description": [
                Statuses.ADDED.name,
                Statuses.DELETED.name,
                Statuses.REPLACED.name,
                Statuses.MODIFIED.name,
                Statuses.NO_DIFF.name,
                Statuses.UNKNOWN.name,
            ],
            "example": [
                {"old_value": {}, "new_value": {"added_key": "value"}},
                {"old_value": {"deleted_key": "value"}, "new_value": {}},
                {
                    "old_value": {"replaced_key": "old-value"},
                    "new_value": {"replaced_key": "new-value"},
                },
                {
                    "old_value": {"modified_key": []},
                    "new_value": {"modified_key": ["value"]},
                },
                {
                    "old_value": {"no_diff_key": "value"},
                    "new_value": {"no_diff_key": "value"},
                },
            ],
        }
