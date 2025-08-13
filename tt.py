from jsonschema_diff.legend_redner import LegendRichTable
from rich import box
from jsonschema_diff.core import Compare
from jsonschema_diff.core.custom_compare.list import CompareList


LegendRichTable.render(
    classes=[Compare, CompareList],
    required=("element", "description", "example"),
    extras=(),
    column_opts={
        "element": {"ratio": 1, "max_width": 40, "overflow": "fold"},
        "description": {"ratio": 2, "max_width": 40, "overflow": "fold"},  # ключевая строка
        "example": {"ratio": 1, "max_width": 40, "overflow": "fold"},
    },
    box_style=box.SQUARE_DOUBLE_HEAD,
    inner_mode="rules",          # ← ключевой пункт
    inner_rule_style=None,       # или "dim"
    inner_rule_chars="─",       # или "─"
    show_lines=True,
    blend_inner_borders=True,
)
