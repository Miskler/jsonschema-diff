# jsonschema_diff/sphinx/directive.py
"""Sphinx directive to embed a Rich‑rendered JSON‑schema diff as SVG.

Usage::

    .. jsonschemadiff:: old.json new.json
       :name:   my_diff.svg   # optional custom file name (".svg" can be omitted)
       :title:  Schema Diff   # title shown inside the virtual terminal tab
       :no-body:             # hide diff body, keep (future) legend only
       :no-legend:           # hide legend, show body only
       :width:  80%          # pass through to the resulting <img> tag

All options are optional; sensible defaults are applied when omitted.
"""
from __future__ import annotations

import hashlib
import inspect
import shutil
from pathlib import Path
from typing import List, Optional, Callable

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from rich.console import Console, Group
from sphinx.errors import ExtensionError
from sphinx.util import fileutil, logging

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
    def run(self) -> List[nodes.Node]:  # noqa: D401 (imperative name is fine)
        env = self.state.document.settings.env
        srcdir = Path(env.srcdir)

        old_path = (srcdir / self.arguments[0]).resolve()
        new_path = (srcdir / self.arguments[1]).resolve()
        if not old_path.exists() or not new_path.exists():
            raise self.error(f"JSON‑schema file not found: {old_path} / {new_path}")

        diff = getattr(env.app.config, "jsonschema_diff", None)
        if diff is None:
            raise ExtensionError(
                "Define variable `jsonschema_diff` (JsonSchemaDiff instance) in conf.py."
            )

        from jsonschema_diff import JsonSchemaDiff  # pylint: disable=import-outside-toplevel

        if not isinstance(diff, JsonSchemaDiff):
            raise ExtensionError("`jsonschema_diff` is not a JsonSchemaDiff instance.")

        # Perform comparison and collect Rich renderables
        diff.compare(str(old_path), str(new_path))
        parts: list = []
        if "no-body" not in self.options:
            parts.append(diff.rich_render())
        # Placeholder for future legend rendering
        # if "no-legend" not in self.options:
        #     parts.append(diff.rich_legend())
        if not parts:
            return []

        console = Console(record=True, width=self._CONSOLE_WIDTH)
        console.print(Group(*parts))

        # Export SVG
        export_kwargs = {
            "title": self.options.get("title", "Rich"),
            "clear": False,
        }
        if "inline_styles" in inspect.signature(console.export_svg).parameters:
            export_kwargs["inline_styles"] = True

        svg_code = console.export_svg(**export_kwargs)

        # Prepare filesystem paths
        static_dir = Path(env.app.srcdir) / self._STATIC_SUBDIR
        if not hasattr(env.app, "_jsonschema_diff_cleaned"):
            shutil.rmtree(static_dir, ignore_errors=True)
            env.app._jsonschema_diff_cleaned = True
        static_dir.mkdir(parents=True, exist_ok=True)

        svg_name = self._make_svg_name(old_path, new_path, console.export_text)
        svg_path = static_dir / svg_name
        svg_path.write_text(svg_code, encoding="utf-8")

        # Ensure asset copied to build directory
        fileutil.copy_asset_file(svg_path, Path(env.app.outdir) / self._STATIC_SUBDIR / svg_name)

        # Build relative URI (works regardless of documentation depth)
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
        custom_name: Optional[str] = self.options.get("name")
        if custom_name and not custom_name.lower().endswith(".svg"):
            custom_name += ".svg"
        if custom_name:
            return custom_name
        digest = hashlib.md5(export_text(clear=False).encode()).hexdigest()[:8]
        return f"{old_path.stem}-{new_path.stem}-{digest}.svg"
