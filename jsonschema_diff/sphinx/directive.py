# jsonschema_diff/sphinx/directive.py
"""Sphinx directive to embed a Rich‑rendered JSON‑schema diff as SVG.

Usage::

    .. jsonschemadiff:: old.json new.json
       :name:   my_diff.svg   # optional custom file name (".svg" can be omitted)
       :title:  Schema Diff   # title shown inside the virtual terminal tab
       :no-body:             # hide diff body, keep legend only
       :no-legend:           # hide legend, show body only
       :width:  80%          # pass through to the resulting <img> tag

All options are optional; sensible defaults are applied when omitted.
"""
from __future__ import annotations

import hashlib
import io
import shutil
from pathlib import Path
from typing import Callable, List, Optional

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from rich.console import Console, Group
from sphinx.errors import ExtensionError
from sphinx.util import logging

__all__ = ["JsonSchemaDiffDirective"]

LOGGER = logging.getLogger(__name__)


class JsonSchemaDiffDirective(Directive):
    """Embed an SVG diff between two JSON‑schema files."""

    has_content = False
    required_arguments = 2  # <old schema> <new schema>
    option_spec = {
        # behaviour flags
        "no-legend": directives.flag,
        "no-body": directives.flag,
        # styling / output options
        "width": directives.unchanged,
        "name": directives.unchanged,
        "title": directives.unchanged,
    }

    _STATIC_SUBDIR = Path("_static") / "jsonschema_diff"
    _CONSOLE_WIDTH = 120

    # ---------------------------------------------------------------------
    def run(self) -> List[nodes.Node]:  # noqa: D401
        env = self.state.document.settings.env
        srcdir = Path(env.srcdir)

        old_path = (srcdir / self.arguments[0]).resolve()
        new_path = (srcdir / self.arguments[1]).resolve()
        if not old_path.exists() or not new_path.exists():
            raise self.error(f"JSON‑schema file not found: {old_path} / {new_path}")

        # ------------------------------------------------------------------
        # Retrieve configured diff object from conf.py
        diff = getattr(env.app.config, "jsonschema_diff", None)
        if diff is None:
            raise ExtensionError(
                "Define variable `jsonschema_diff` (JsonSchemaDiff instance) in conf.py."
            )

        from jsonschema_diff import JsonSchemaDiff  # pylint: disable=import-outside-toplevel

        if not isinstance(diff, JsonSchemaDiff):
            raise ExtensionError("`jsonschema_diff` is not a JsonSchemaDiff instance.")

        # ------------------------------------------------------------------
        # Produce Rich renderables
        diff.compare(str(old_path), str(new_path))
        renderables: list = []
        body = diff.rich_render()
        if "no-body" not in self.options:
            renderables.append(body)
        if "no-legend" not in self.options and hasattr(diff, "rich_legend"):
            renderables.append(diff.rich_legend(diff.last_compare_list))
        if not renderables:
            return []

        # ------------------------------------------------------------------
        # Use Rich to create SVG
        console = Console(record=True, width=self._CONSOLE_WIDTH, file=io.StringIO())
        console.print(Group(*renderables))

        export_kwargs = {
            "title": self.options.get("title", "Rich"),
            "clear": False,
        }

        svg_code = console.export_svg(**export_kwargs)

        # ------------------------------------------------------------------
        # Save SVG to _static/jsonschema_diff
        static_dir = Path(env.app.srcdir) / self._STATIC_SUBDIR
        if not hasattr(env.app, "_jsonschema_diff_cleaned"):
            shutil.rmtree(static_dir, ignore_errors=True)
            env.app._jsonschema_diff_cleaned = True
        static_dir.mkdir(parents=True, exist_ok=True)

        svg_name = self._make_svg_name(old_path, new_path, console.export_text)
        svg_path = static_dir / svg_name
        svg_path.write_text(svg_code, encoding="utf-8")

        # ------------------------------------------------------------------
        # Insert <img> node with correct relative URI
        doc_depth = env.docname.count("/")
        uri_prefix = "../" * doc_depth
        img_uri = f"{uri_prefix}_static/jsonschema_diff/{svg_name}"

        img_node = nodes.image(uri=img_uri, alt=f"diff {old_path.name}")
        if "width" in self.options:
            img_node["width"] = self.options["width"]
        return [img_node]

    # ------------------------------------------------------------------
    def _make_svg_name(
        self,
        old_path: Path,
        new_path: Path,
        export_text: Callable,
    ) -> str:
        """Return custom name (if provided) or deterministic hash‑based name."""
        custom_name: Optional[str] = self.options.get("name")
        if custom_name and not custom_name.lower().endswith(".svg"):
            custom_name += ".svg"
        if custom_name:
            return custom_name
        digest = hashlib.md5(export_text(clear=False).encode()).hexdigest()[:8]
        return f"{old_path.stem}-{new_path.stem}-{digest}.svg"
