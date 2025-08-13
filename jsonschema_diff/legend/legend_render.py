from typing import Iterable, Sequence, Mapping, Any, List, Optional, Tuple, Callable
from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich.rule import Rule
from rich import box

ColumnProcessor = Callable[..., Any]  # должен вернуть str или list[str]

class LegendRichTable:
    @staticmethod
    def _apply_processor(col: str, val: Any, processors: Mapping[str, ColumnProcessor] | None) -> Any:
        if not processors or col not in processors:
            return val
        fn = processors[col]
        if isinstance(val, dict):
            return fn(**val)
        elif isinstance(val, (list, tuple)):
            return fn(*val)
        else:
            return fn(val)

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
        # str / None → как есть
        if value is None or isinstance(value, str):
            return ("" if value is None else value), False

        # list[str] → вложенный «список» с разделителями между пунктами
        if isinstance(value, (list, tuple)) and all(isinstance(x, str) for x in value):
            if not nested_lists_as_subtable:
                return "\n".join(value), False

            if inner_mode == "rules":
                inner = Table.grid(expand=True, padding=(0, 0))
                inner.add_column(justify=inner_justify, ratio=1, overflow="fold")
                first = True
                for s in value:
                    if not first:
                        # Без цвета; верхнюю линию не добавляем — только между пунктами
                        kw = {"style": "none"} if inner_rule_style is None else {"style": inner_rule_style}
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
        table_width: Optional[int] = None,         # общий предел ширины (для распределения ratio)
        show_lines: bool = False,
        nested_lists_as_subtable: bool = True,
        inner_mode: str = "rules",
        inner_justify: str = "left",
        inner_rule_style: Optional[str] = None,    # None => "none" (без цвета)
        inner_rule_chars: Optional[str] = None,    # напр. "─"
        blend_inner_borders: bool = True,
        default_overflow: str = "fold",
        # управление колонками
        ratios: Optional[Mapping[str, int]] = None,           # {"col": 2, ...}
        no_wrap_columns: Sequence[str] = (),
        column_processors: Optional[Mapping[str, ColumnProcessor]] = None,  # {"example": func}
    ) -> str:
        if len(required) != 3:
            raise ValueError("Нужно ровно 3 обязательных столбца в 'required'.")

        # Сбор и валидация легенд
        collected: List[Mapping[str, Any]] = []
        for cls in classes:
            legend = cls.legend()
            if not isinstance(legend, Mapping):
                raise TypeError(f"{cls.__name__}.legend() должен вернуть dict")
            LegendRichTable._validate_required(cls, legend, required)
            collected.append(legend)

        # Колонки
        columns = list(required) + list(extras)
        if auto_extras:
            seen = set(columns)
            for legend in collected:
                for k in legend.keys():
                    if k not in seen:
                        columns.append(k); seen.add(k)

        # Внешняя таблица: expand=True + width=table_width => ratio реально работает
        table = Table(
            show_header=True,
            header_style=header_style,
            box=box_style,
            padding=(0, 0) if blend_inner_borders else (0, 1),
            show_lines=show_lines,
            expand=True,
            width=table_width,   # можно None — тогда займёт ширину консоли
        )

        # Колонки с ratio/overflow/no_wrap/justify
        for key in columns:
            header = headers_alias.get(key, key) if headers_alias else key
            j = (justify or {}).get(key, "left")
            r = (ratios or {}).get(key, None)
            table.add_column(
                header,
                justify=j,
                ratio=r,                      # работает при expand=True
                overflow=default_overflow,
                no_wrap=(key in set(no_wrap_columns)),
            )

        # Строки
        for legend in collected:
            row_cells = []
            for k in columns:
                raw_val = legend.get(k, "")
                # прогон через пользовательский обработчик колонки (если есть)
                processed = LegendRichTable._apply_processor(k, raw_val, column_processors)

                renderable, is_nested = LegendRichTable._to_cell_renderable(
                    processed,
                    nested_lists_as_subtable=nested_lists_as_subtable,
                    inner_mode=inner_mode,
                    inner_justify=inner_justify,
                    inner_rule_style=inner_rule_style,
                    inner_rule_chars=inner_rule_chars,
                )
                cell = renderable if (blend_inner_borders and is_nested) else Padding(renderable, (0, 1))
                row_cells.append(cell)

            table.add_row(*row_cells)

        console = Console(record=True, force_terminal=True, width=table_width)
        console.print(table)
        return console.export_text()
