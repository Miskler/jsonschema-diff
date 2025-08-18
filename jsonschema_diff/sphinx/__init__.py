# jsonschema_diff/sphinx/__init__.py
"""
Sphinx extension: ``jsonschema_diff.sphinx``

Директива::

    .. jsonschemadiff:: old.schema.json new.schema.json
       :no-legend:   # убрать легенду
       :no-body:     # показать только легенду
       :width: 90%   # ширина вставляемого SVG

В ``conf.py`` проекта ОБЯЗАТЕЛЬНО объявить переменную
``jsonschema_diff`` — готовый экземпляр :class:`JsonSchemaDiff`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sphinx.application import Sphinx


def setup(app: Sphinx) -> dict[str, Any]:
    """Регистрация директивы и конфигурационной переменной."""
    from .directive import JsonSchemaDiffDirective

    app.add_directive("jsonschemadiff", JsonSchemaDiffDirective)

    # единственная настраиваемая переменная
    app.add_config_value("jsonschema_diff", None, "env")

    # гарантируем наличие _static в html_static_path
    static_root = Path(app.srcdir) / "_static"
    if str(static_root) not in app.config.html_static_path:
        app.config.html_static_path.append(str(static_root))

    return {
        "version": "0.4.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
