from jsonschema_diff.legend.legend_render import LegendRichTable
from rich import box
from jsonschema_diff.core import Compare
from jsonschema_diff.core.custom_compare.list import CompareList


LegendRichTable.render(
    classes=[Compare, CompareList],
    required=("element", "description", "example"),
    extras=(),
    column_opts={
        "element": {"max_width": 40, "overflow": "fold"},
        "description": {"max_width": 40, "overflow": "fold"},  # ключевая строка
        "example": {"max_width": 40, "overflow": "fold"},
    },
    box_style=box.SQUARE_DOUBLE_HEAD,
    inner_mode="rules",          # ← ключевой пункт
    inner_rule_style=None,       # или "dim"
    inner_rule_chars="─",       # или "─"
    show_lines=True,
    blend_inner_borders=True,
)
