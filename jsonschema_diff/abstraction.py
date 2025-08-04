from enum import Enum

class Statuses(Enum):
    ADDED    = "+"
    DELETED  = "-"
    REPLACED = "r"
    MODIFIED = "m"
    NO_DIFF  = " "
    UNKNOWN  = "?"
