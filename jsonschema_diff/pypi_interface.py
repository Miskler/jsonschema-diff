"""
Thin wrapper that exposes a simpler, Pandas-free API for PyPI users.

It delegates heavy lifting to :class:`jsonschema_diff.core.Property` and
applies optional ANSI-color highlighting.
"""

from json import loads
from typing import Optional

from rich.table import Table
from rich.text import Text

from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.core import Compare, Config, Property
from jsonschema_diff.table_render import LegendRenderer, make_standard_renderer


class JsonSchemaDiff:
    """
    Facade around the low-level diff engine.

    Call sequence
    -------------
    1. :meth:`compare` or :meth:`compare_from_files`
    2. :meth:`render` → string (kept in *last_render_output*)
    3. :meth:`legend` → legend table (uses *last_compare_list*)
    """

    def __init__(
        self,
        config: Config,
        colorize_pipeline: HighlighterPipeline,
        legend_ignore: list[type[Compare]] | None = None,
    ):
        self.config: Config = config
        self.colorize_pipeline: HighlighterPipeline = colorize_pipeline
        self.table_maker: LegendRenderer = make_standard_renderer(
            example_processor=self._example_processor, table_width=90
        )
        self.legend_ignore: list[type[Compare]] = legend_ignore or []

        self.last_render_output: str = ""
        self.last_compare_list: list[type[Compare]] = []

    # ------------------------------------------------------------------ #
    # Static helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _schema_resolver(schema: str | dict) -> dict:
        if isinstance(schema, dict):
            return schema
        else:
            with open(schema, "r", encoding="utf-8") as fp:
                return dict(loads(fp.read()))

    @staticmethod
    def fast_pipeline(
        config: "Config",
        old_schema: dict | str,
        new_schema: dict | str,
        colorize_pipeline: Optional["HighlighterPipeline"],
    ) -> tuple[str, list[type[Compare]]]:
        """
        One-shot utility: compare *old_schema* vs *new_schema* and
        return ``(rendered_text, compare_list)``.

        Accepted formats: dict or path to JSON file.
        """
        prop = Property(
            config=config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=JsonSchemaDiff._schema_resolver(old_schema),
            new_schema=JsonSchemaDiff._schema_resolver(new_schema),
        )
        prop.compare()
        output_text, compare_list = prop.render()
        rendered_text = "\n\n".join(output_text)

        if colorize_pipeline is not None:
            rendered_text = colorize_pipeline.colorize_and_render(rendered_text)

        return rendered_text, compare_list

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def compare(self, old_schema: dict | str, new_schema: dict | str) -> "JsonSchemaDiff":
        """Populate internal :class:`Property` tree and perform comparison.

        Accepted formats: dict or path to JSON file."""

        self.property = Property(
            config=self.config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=JsonSchemaDiff._schema_resolver(old_schema),
            new_schema=JsonSchemaDiff._schema_resolver(new_schema),
        )
        self.property.compare()
        return self

    def rich_render(self) -> Text:
        """
        Return the diff body ANSI-colored.

        Side effects
        ------------
        * ``self.last_render_output`` – cached rendered text.
        * ``self.last_compare_list`` – list of Compare subclasses encountered.
        """
        body, compare_list = self.property.render()
        self.last_render_output = "\n\n".join(body)
        self.last_compare_list = compare_list

        return self.colorize_pipeline.colorize(self.last_render_output)

    def render(self) -> str:
        """
        Return the diff body ANSI-colored.

        Side effects
        ------------
        * ``self.last_render_output`` – cached rendered text.
        * ``self.last_compare_list`` – list of Compare subclasses encountered.
        """
        body, compare_list = self.property.render()
        self.last_render_output = "\n\n".join(body)
        self.last_compare_list = compare_list

        return self.colorize_pipeline.colorize_and_render(self.last_render_output)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _example_processor(self, old_value: dict, new_value: dict) -> Text:
        """
        Callback for :pyfunc:`~jsonschema_diff.table_render.make_standard_renderer`
        that renders inline examples.
        """
        output, _ = JsonSchemaDiff.fast_pipeline(self.config, old_value, new_value, None)
        return self.colorize_pipeline.colorize(output)

    # ------------------------------------------------------------------ #
    # Legend & printing
    # ------------------------------------------------------------------ #

    def rich_legend(self, comparators: list[type[Compare]]) -> Table:
        """Return a legend table filtered by *self.legend_ignore*."""
        real = [c for c in comparators if c not in self.legend_ignore]
        return self.table_maker.rich_render(real)

    def legend(self, comparators: list[type[Compare]]) -> str:
        """Return a legend table filtered by *self.legend_ignore*."""
        real = [c for c in comparators if c not in self.legend_ignore]
        return self.table_maker.render(real)

    def print(
        self,
        *,
        with_body: bool = True,
        with_legend: bool = True,
    ) -> None:
        """
        Pretty-print the diff and/or the legend.

        Parameters
        ----------
        colorized : bool
            Apply ANSI colors to both body and legend.
        with_body, with_legend : bool
            Toggle respective sections.
        """
        if with_body:
            print(self.render())

        if with_body and with_legend:
            print()

        if with_legend:
            print(self.legend(self.last_compare_list))
