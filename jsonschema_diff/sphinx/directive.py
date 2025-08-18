# jsonschema_diff/sphinx/directive.py
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from rich.console import Console, Group
from sphinx.errors import ExtensionError
from sphinx.util import logging

LOGGER = logging.getLogger(__name__)


class JsonSchemaDiffDirective(Directive):
    """
    .. jsonschemadiff:: old.json new.json
       :no-legend:
       :no-body:
       :width: 80%
    """

    has_content = False
    required_arguments = 2
    option_spec = {
        "no-legend": directives.flag,
        "no-body":   directives.flag,
        "width":     directives.unchanged,
    }

    # ------------------------------------------------------------------ #
    def run(self) -> List[nodes.Node]:
        env    = self.state.document.settings.env
        srcdir = Path(env.srcdir)

        old_path = (srcdir / self.arguments[0]).resolve()
        new_path = (srcdir / self.arguments[1]).resolve()
        if not old_path.exists() or not new_path.exists():
            raise self.error(
                f"JSON Schema file not found: {old_path} / {new_path}"
            )

        # ─── берём настроенный экземпляр из conf.py ─────────────────────
        diff = getattr(env.app.config, "jsonschema_diff", None)
        if diff is None:
            raise ExtensionError(
                "Define variable `jsonschema_diff` (JsonSchemaDiff instance) "
                "in your conf.py."
            )

        from jsonschema_diff import JsonSchemaDiff  # локальный импорт
        if not isinstance(diff, JsonSchemaDiff):
            raise ExtensionError(
                "Variable `jsonschema_diff` is not an instance of JsonSchemaDiff."
            )

        # ─── считаем diff ───────────────────────────────────────────────
        diff.compare(str(old_path), str(new_path))

        want_body   = "no-body"   not in self.options
        want_legend = "no-legend" not in self.options

        # Rich-объекты, готовые к печати
        rich_parts = []
        if want_body:
            rich_parts.append(diff.rich_render())
        if want_legend:
            rich_parts.append(diff.rich_legend(diff.last_compare_list))

        if not rich_parts:                     # ничего не выводить?
            return []

        # ─── Rich → SVG (по сути “сфотографируем” вывод консоли) ───────
        console = Console(record=True, width=120)
        console.print(Group(*rich_parts))

        svg_dir  = Path(env.app.srcdir) / "_static" / "jsonschema_diff"
        svg_dir.mkdir(parents=True, exist_ok=True)

        # сделаем хэш-имя, чтобы кэш корректно инвалидировался
        digest   = hashlib.md5(console.export_text(clear=False).encode()).hexdigest()[:8]
        svg_name = f"{old_path.stem}-{new_path.stem}-{digest}.svg"
        svg_path = svg_dir / svg_name

        console.save_svg(str(svg_path), title=svg_name)

        # ─── вставляем картинку в документ ──────────────────────────────
        img_uri = f"/_static/jsonschema_diff/{svg_name}"
        node = nodes.image(uri=img_uri, alt=f"diff {old_path.name}")
        if "width" in self.options:
            node["width"] = self.options["width"]

        LOGGER.debug("[jsonschema-diff] rendered %s → %s", old_path.name, svg_name)
        return [node]
