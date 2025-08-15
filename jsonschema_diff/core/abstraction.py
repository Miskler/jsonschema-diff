from enum import Enum
from typing import Any


class Statuses(Enum):
    ADDED = "+"
    DELETED = "-"
    REPLACED = "r"
    MODIFIED = "m"
    NO_DIFF = " "
    UNKNOWN = "?"


class ToCompare:
    def __init__(
        self, old_key: str | None, old_value: Any, new_key: str | None, new_value: Any
    ) -> None:
        self.old_key = old_key
        self.old_value = old_value
        self.new_key = new_key
        self.new_value = new_value

        if old_key is None and new_key is not None:
            self.status = Statuses.ADDED
            self.key = new_key
            self.value = new_value
        elif old_key is not None and new_key is None:
            self.status = Statuses.DELETED
            self.key = old_key
            self.value = old_value
        elif old_key is not None and new_key is not None:
            if str(new_value) == str(old_value):
                self.status = Statuses.NO_DIFF
            else:
                self.status = Statuses.REPLACED

            self.key = new_key
            self.value = new_value
        else:
            raise ValueError(
                "Cannot compare None to None: "
                f"`{old_key}: {type(old_value).__name__} = {old_value}` -> "
                f"`{new_key}: {type(new_value).__name__} = {new_value}`"
            )

    def __repr__(self) -> str:
        return (
            "ToCompare("
            f"key={self.key}, old_value={self.old_value}, "
            f"new_value={self.new_value}, status={self.status.name})"
        )
