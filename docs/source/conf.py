# docs/source/conf.py
from __future__ import annotations
import sys, os, importlib
from pathlib import Path
from docutils.parsers.rst import roles
from sphinx.roles import XRefRole

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]          # repo root
sys.path.insert(0, str(ROOT))                       # import project without install

# ──────────────────────────────────────────────────────────────────────────────
# Project meta
# ──────────────────────────────────────────────────────────────────────────────
project   = "jsonschema-diff"
author    = "Miskler"
copyright = "2026, Miskler"
from jsonschema_diff import __version__
release   = __version__

# ──────────────────────────────────────────────────────────────────────────────
# Extensions
# ──────────────────────────────────────────────────────────────────────────────
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "autoapi.extension",
    "jsonschema_diff.sphinx",
]

# ──────────────────────────────────────────────────────────────────────────────
# Theme / HTML
# ──────────────────────────────────────────────────────────────────────────────
html_theme       = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo_day.png",
    "dark_logo": "logo_night.png",
    "sidebar_hide_name": True,

    "source_repository": "https://github.com/Miskler/jsonschema-diff",
    "source_branch": "main",
    "source_directory": "docs/",
}
templates_path   = ["_templates"]

# ──────────────────────────────────────────────────────────────────────────────
# Навигация и compact-style
# ──────────────────────────────────────────────────────────────────────────────
add_module_names                     = False        # compare() → Config
toc_object_entries_show_parents      = "hide"       # короче TOC
python_use_unqualified_type_names    = True         # Config, а не jsonschema_diff.core.Config
multi_line_parameter_list            = True         # каждый аргумент с новой строки
python_maximum_signature_line_length = 60           # длина, после которой рвём строку

# ──────────────────────────────────────────────────────────────────────────────
# Type-hints
# ──────────────────────────────────────────────────────────────────────────────
autodoc_typehints = "signature"      # str / Dict[...] остаются в сигнатуре
typehints_fqcn    = False            # короткие имена в хинтах

# ──────────────────────────────────────────────────────────────────────────────
# AutoAPI – строим flat API Reference
# ──────────────────────────────────────────────────────────────────────────────
autoapi_type              = "python"
autoapi_dirs              = [str(ROOT / "jsonschema_diff")]
autoapi_root              = "reference/api"
autoapi_add_toctree_entry = True
autoapi_python_use_implicit_namespaces = True

autoapi_options = [
    "members",
    "undoc-members",
    #"private-members",
    "show-module-summary",
    "special-members",
    "imported-members"
]

# ──────────────────────────────────────────────────────────────────────────────
# Intersphinx – ссылки на stdlib / typing
# ──────────────────────────────────────────────────────────────────────────────
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
}

# ──────────────────────────────────────────────────────────────────────────────
# jsonschema-diff highlight pipeline (без изменений)
# ──────────────────────────────────────────────────────────────────────────────
from jsonschema_diff import ConfigMaker, JsonSchemaDiff
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter, PathHighlighter, ReplaceGenericHighlighter,
)

jsonschema_diff = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline(
        [MonoLinesHighlighter(), ReplaceGenericHighlighter(), PathHighlighter()],
    ),
)

# ──────────────────────────────────────────────────────────────────────────────
# Extra hooks
# ──────────────────────────────────────────────────────────────────────────────

ALIASES = {
    "Compare":  "jsonschema_diff.core.parameter_base",
    "Statuses": "jsonschema_diff.core.abstraction",
    "Config":   "jsonschema_diff.core.config",
}

def skip_canon(app, what, name, obj, skip, options):
    short = name.rsplit(".", 1)[-1]
    # если имя в списке и мы сейчас документируем канонический модуль — пропустить
    if short in ALIASES and name.startswith(ALIASES[short]):
        return True
    return skip


def setup(app):
    app.connect("autoapi-skip-member", skip_canon)
    app.add_role("pyclass", XRefRole("class"))
    app.add_role("pyfunc", XRefRole("func"))
