"""Clean, modular implementation of rich-based legend tables (v2).

Changes v2
-----------
* **Robust renderable detection** – supports returning any Rich renderable
  (Text, Panel, Table, etc.) directly from a column‑processor.
* ANSI bleed fixed: we never coerce unknown objects to `str`; if value
  isn't recognised we call `repr()` (safe, no control codes).
* Lists can mix str **and** Rich renderables – all rendered in a nested
  grid with rules between blocks.
* Helper `ColumnConfig.wrap=False` to suppress cell padding when
  renderable already has its own framing (e.g. Panel).
* Ratio now respected (outer `Table(expand=True, width=table_width)`),
  still no `max_width`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterable, Literal, Mapping, Sequence, Union, cast

if TYPE_CHECKING:
    from .core.compare_base import Compare

from rich import box
from rich.console import Console, RenderableType
from rich.padding import Padding
from rich.rule import Rule
from rich.table import Table

StrOrRenderable = Union[str, RenderableType]
Processor = Callable[..., StrOrRenderable | list[StrOrRenderable]]


def _is_rich_renderable(obj: Any) -> bool:
    """Heuristic: object implements Rich render protocol."""
    return hasattr(obj, "__rich_console__") or hasattr(obj, "__rich_measure__")


@dataclass(slots=True)
class ColumnConfig:
    name: str
    header: str | None = None
    ratio: float | None = None
    justify: str = "left"
    no_wrap: bool = False
    wrap: bool = True  # add Padding around the cell
    processor: Processor | None = None

    def header_text(self) -> str:
        return self.header or self.name


@dataclass(slots=True)
class Cell:
    """Display‑ready cell."""

    value: RenderableType
    pad: bool = True  # if False – value already framed (Panel/Table)

    def renderable(self) -> RenderableType:
        if self.pad:
            return Padding(self.value, (0, 1))
        return self.value


class LegendRenderer:
    """Facade to build a table from legend classes."""

    def __init__(
        self,
        columns: Sequence[ColumnConfig],
        *,
        box_style: box.Box = box.SQUARE_DOUBLE_HEAD,
        header_style: str = "bold",
        table_width: int | None = None,
        show_outer_lines: bool = True,
        default_overflow: str = "fold",
    ) -> None:
        self.columns = list(columns)
        self.box_style = box_style
        self.header_style = header_style
        self.table_width = table_width
        self.show_outer_lines = show_outer_lines
        self.default_overflow = default_overflow

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rich_render(self, legend_classes: Iterable[type["Compare"]]) -> Table:
        legends = [cls.legend() for cls in legend_classes]
        self._validate_legends(legends)

        rows: list[list[Cell]] = [self._build_row(legend) for legend in legends]
        return self._build_table(rows)

    def render(self, legend_classes: Iterable[type["Compare"]]) -> str:
        table = self.rich_render(legend_classes)

        # Use a throw‑away Console so we don't affect the caller's Console config
        console = Console(
            force_terminal=True,  # ensure ANSI codes even when not attached to tty
            color_system="truecolor",
            width=self.table_width,  # avoid unwanted wrapping
            legacy_windows=False,
        )

        with console.capture() as cap:
            console.print(table, end="")  # prevent extra newline
        return cap.get()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _validate_legends(self, legends: Sequence[Mapping[str, Any]]) -> None:
        required = {c.name for c in self.columns}
        for i, legend in enumerate(legends):
            missing = required - legend.keys()
            if missing:
                raise KeyError(f"Legend #{i} missing keys: {', '.join(missing)}")

    # ---------- building ------------------------------------------------

    def _build_row(self, legend: Mapping[str, Any]) -> list[Cell]:
        row: list[Cell] = []
        for col in self.columns:
            raw = legend.get(col.name, "")
            processed = self._apply_processor(raw, col.processor)
            cell = self._make_cell(processed, pad=col.wrap, justify=col.justify)
            row.append(cell)
        return row

    def _apply_processor(self, value: Any, processor: Processor | None) -> Any:
        if processor is None:
            return value
        if value in (None, "", [], ()):
            return value
        if isinstance(value, dict):
            return processor(**value)
        if isinstance(value, (list, tuple)):
            processed: list[Any] = []
            for item in value:
                if isinstance(item, dict):
                    processed.append(processor(**item))
                elif isinstance(item, (list, tuple)):
                    processed.append(processor(*item))
                else:
                    processed.append(processor(item))
            return processed
        return processor(value)

    def _make_cell(self, data: Any, *, pad: bool, justify: str = "left") -> Cell:
        # Direct rich renderable
        if _is_rich_renderable(data):
            return Cell(data, pad=pad)

        # Primitive str / None
        if data is None or isinstance(data, str):
            return Cell("" if data is None else data, pad=pad)

        # list / tuple – may mix str & renderables
        if isinstance(data, (list, tuple)):
            sub = Table.grid(expand=True, padding=(0, 0))
            sub.add_column(
                ratio=1,
                justify=cast(Literal["default", "left", "center", "right", "full"], justify),
                overflow="fold",
            )
            first = True
            for item in data:
                if not first:
                    sub.add_row(Rule(style="none", characters="─"))
                sub.add_row(item if _is_rich_renderable(item) else str(item))
                first = False
            return Cell(sub, pad=False)  # already framed

        # Fallback – safe repr (no ANSI leak)
        return Cell(repr(data), pad=pad)

    def _build_table(self, rows: Sequence[Sequence[Cell]]) -> Table:
        tbl = Table(
            show_header=True,
            header_style=self.header_style,
            box=self.box_style,
            padding=(0, 0),
            show_lines=self.show_outer_lines,
            expand=True,
            width=self.table_width,
        )
        for col in self.columns:
            tbl.add_column(
                col.header_text(),
                justify=cast(Literal["default", "left", "center", "right", "full"], col.justify),
                ratio=None if col.ratio is None else int(col.ratio),
                no_wrap=col.no_wrap,
                overflow=cast(Literal["fold", "crop", "ellipsis", "ignore"], self.default_overflow),
            )

        for r in rows:
            tbl.add_row(*[c.renderable() for c in r])
        return tbl


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def make_standard_renderer(
    *,
    example_processor: Processor | None = None,
    table_width: int | None = None,
) -> LegendRenderer:
    columns = [
        ColumnConfig("element", header="Element", justify="center", ratio=1),
        ColumnConfig("description", header="Description", justify="center", ratio=2),
        ColumnConfig(
            "example",
            header="Diff Example",
            ratio=2.5,
            processor=example_processor,
            wrap=False,
        ),
    ]
    return LegendRenderer(columns, table_width=table_width)
