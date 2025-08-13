from typing import Iterable, Sequence, Mapping, Any, List, Optional, Tuple
from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich.rule import Rule
from rich import box

class LegendRichTable:
    @staticmethod
    def _to_cell_renderable(
        value: Any,
        *,
        nested_lists_as_subtable: bool,
        inner_mode: str,
        inner_justify: str,
        inner_rule_style: Optional[str],
        inner_rule_chars: Optional[str],
    ):
        if value is None or isinstance(value, str):
            return ("" if value is None else value), False

        if isinstance(value, (list, tuple)) and all(isinstance(x, str) for x in value):
            if not nested_lists_as_subtable:
                return "\n".join(value), False

            if inner_mode == "rules":
                inner = Table.grid(expand=True, padding=(0, 0))
                inner.add_column(justify=inner_justify, ratio=1, overflow="fold")
                first = True
                for s in value:
                    if not first:
                        # Без цвета и без верхней линии
                        kw = {}
                        # по умолчанию отключаем цвет: style="none"
                        kw["style"] = "none" if inner_rule_style is None else inner_rule_style
                        if inner_rule_chars is not None:
                            kw["characters"] = inner_rule_chars
                        inner.add_row(Rule(**kw))
                    inner.add_row(s)
                    first = False
                return inner, True

            elif inner_mode == "horizontals":
                inner = Table(show_header=False, box=box.HORIZONTALS, padding=(0, 0), show_lines=True, expand=True)
                inner.add_column(justify=inner_justify, ratio=1, overflow="fold")
                for s in value:
                    inner.add_row(s)
                return inner, True

        raise TypeError("Значение ячейки должно быть str или списком str")

    @staticmethod
    def _validate_required(cls: type, legend: Mapping[str, Any], required: Sequence[str]) -> None:
        missing = [k for k in required if k not in legend]
        if missing:
            raise KeyError(f"{cls.__name__}.legend(): нет ключей {', '.join(missing)}")

    @staticmethod
    def render(
        classes: Iterable[type],
        required: Sequence[str],
        extras: Sequence[str] = (),
        *,
        auto_extras: bool = False,
        headers_alias: Optional[Mapping[str, str]] = None,
        justify: Optional[Mapping[str, str]] = None,
        box_style = box.SQUARE_DOUBLE_HEAD,
        header_style: str = "bold",
        table_width: Optional[int] = None,         # ← глобальный лимит ширины
        show_lines: bool = False,
        nested_lists_as_subtable: bool = True,
        inner_mode: str = "rules",                 # "rules" — без верхней линии
        inner_justify: str = "left",
        inner_rule_style: Optional[str] = None,    # None => style="none" (без цвета)
        inner_rule_chars: Optional[str] = None,    # напр. "─"
        blend_inner_borders: bool = True,
        # опции колонок (при необходимости): ratio/min_width/max_width/overflow/no_wrap/width/justify
        column_opts: Optional[Mapping[str, Mapping[str, Any]]] = None,
        default_overflow: str = "fold",            # дефолтный перенос для всех колонок
    ) -> str:
        if len(required) != 3:
            raise ValueError("Нужно ровно 3 обязательных столбца в 'required'.")

        collected: List[Mapping[str, Any]] = []
        for cls in classes:
            legend = cls.legend()
            if not isinstance(legend, Mapping):
                raise TypeError(f"{cls.__name__}.legend() должен вернуть dict")
            LegendRichTable._validate_required(cls, legend, required)
            collected.append(legend)

        columns = list(required) + list(extras)
        if auto_extras:
            seen = set(columns)
            for legend in collected:
                for k in legend.keys():
                    if k not in seen:
                        columns.append(k); seen.add(k)

        # Внешняя таблица: БЕЗ expand, иначе max_width колонок игнорится
        table = Table(
            show_header=True,
            header_style=header_style,
            box=box_style,
            padding=(0, 0) if blend_inner_borders else (0, 1),
            show_lines=show_lines,
            expand=False,                 # критично
            width=table_width,            # глобальный лимит
        )

        for key in columns:
            header = headers_alias.get(key, key) if headers_alias else key
            j = (justify or {}).get(key, "left")
            opts = dict((column_opts or {}).get(key, {}))
            j = opts.pop("justify", j)
            # дефолт: перенос (fold), если не переопределён
            opts.setdefault("overflow", default_overflow)
            kwargs = {"justify": j}
            for k_opt in ("ratio", "min_width", "max_width", "overflow", "no_wrap", "width"):
                if k_opt in opts and opts[k_opt] is not None:
                    kwargs[k_opt] = opts[k_opt]
            table.add_column(header, **kwargs)

        for legend in collected:
            row_cells = []
            for k in columns:
                renderable, is_nested = LegendRichTable._to_cell_renderable(
                    legend.get(k, ""),
                    nested_lists_as_subtable=nested_lists_as_subtable,
                    inner_mode=inner_mode,
                    inner_justify=inner_justify,
                    inner_rule_style=inner_rule_style,
                    inner_rule_chars=inner_rule_chars,
                )
                cell = renderable if (blend_inner_borders and is_nested) else Padding(renderable, (0, 1))
                row_cells.append(cell)
            table.add_row(*row_cells)

        console = Console(record=True, force_terminal=True, width=table_width)  # ширина вывода = глобальный лимит
        console.print(table)
        return console.export_text()
