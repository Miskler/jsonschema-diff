"""
Thin wrapper that exposes a simpler, Pandas-free API for PyPI users.

It delegates heavy lifting to :class:`jsonschema_diff.core.Property` and
applies optional ANSI-color highlighting.
"""

from json import loads
from typing import Optional

from rich.text import Text

from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.core import Compare, Config, Property
from jsonschema_diff.table_render import make_standard_renderer


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
        config: "Config",
        colorize_pipeline: "HighlighterPipeline",
        legend_ignore: list[type[Compare]] | None = None,
    ):
        self.config = config
        self.colorize_pipeline = colorize_pipeline
        self.table_maker = make_standard_renderer(
            example_processor=self._example_processor, table_width=90
        )
        self.legend_ignore: list[type[Compare]] = legend_ignore or []

        self.last_render_output: str = ""
        self.last_compare_list: list[type[Compare]] = []

    # ------------------------------------------------------------------ #
    # Static helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def fast_pipeline(
        config: "Config",
        old_schema: dict,
        new_schema: dict,
        colorize_pipeline: Optional["HighlighterPipeline"],
    ) -> tuple[str, list[type[Compare]]]:
        """
        One-shot utility: compare *old_schema* vs *new_schema* and
        return ``(rendered_text, compare_list)``.
        """
        prop = Property(
            config=config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=old_schema,
            new_schema=new_schema,
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

    def compare_from_files(self, old_file_path: str, new_file_path: str) -> "JsonSchemaDiff":
        """Load two files (JSON) and run :meth:`compare`."""
        with (
            open(old_file_path, "r", encoding="utf-8") as fp_old,
            open(new_file_path, "r", encoding="utf-8") as fp_new,
        ):
            return self.compare(
                old_schema=loads(fp_old.read()),
                new_schema=loads(fp_new.read()),
            )

    def compare(self, *, old_schema: dict, new_schema: dict) -> "JsonSchemaDiff":
        """Populate internal :class:`Property` tree and perform comparison."""
        self.property = Property(
            config=self.config,
            name=None,
            schema_path=[],
            json_path=[],
            old_schema=old_schema,
            new_schema=new_schema,
        )
        self.property.compare()
        return self

    def render(self, *, colorized: bool = True) -> str:
        """
        Return the diff body (ANSI-colored if *colorized*).

        Side effects
        ------------
        * ``self.last_render_output`` – cached rendered text.
        * ``self.last_compare_list`` – list of Compare subclasses encountered.
        """
        body, compare_list = self.property.render()
        self.last_render_output = "\n\n".join(body)
        self.last_compare_list = compare_list

        if colorized:
            return self.colorize_pipeline.colorize_and_render(self.last_render_output)
        return self.last_render_output

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

    def legend(self, comparators: list[type[Compare]]) -> str:
        """Return a legend table filtered by *self.legend_ignore*."""
        real = [c for c in comparators if c not in self.legend_ignore]
        return self.table_maker.render(real)

    def print(
        self,
        *,
        colorized: bool = True,
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
            print(self.render(colorized=colorized))

        if with_body and with_legend:
            print()

        if with_legend:
            print(self.legend(self.last_compare_list))
