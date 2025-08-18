# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from pathlib import Path
import json
from rich.console import Console


# -- Path setup --------------------------------------------------------------
# Allow importing the project without installation.
sys.path.insert(0, os.path.abspath("../.."))

from jsonschema_diff import ConfigMaker, JsonSchemaDiff
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter,
    PathHighlighter,
    ReplaceGenericHighlighter,
)
from docutils.parsers.rst import roles
from sphinx.roles import XRefRole


# -- Project information -----------------------------------------------------

project = "jsonschema-diff"
copyright = "2025, Miskler"
author = "Miskler"
release = "0.1.0"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "jsonschema_diff.sphinx",
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns: list[str] = []



jsonschema_diff = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline(
        [MonoLinesHighlighter(), ReplaceGenericHighlighter(), PathHighlighter()]
    ),
)


# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]


# -- Dynamic documentation builders -----------------------------------------

def run_apidoc(app: "Sphinx") -> None:
    """Invoke sphinx-apidoc to build API reference."""
    root = Path(app.confdir).resolve().parent.parent
    module_dir = root / "jsonschema_diff"
    out_dir = Path(app.confdir) / "reference" / "api"
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx.ext.apidoc",
            "-o",
            str(out_dir),
            str(module_dir),
        ],
        check=True,
    )


def setup(app: "Sphinx") -> None:
    roles.register_local_role("pyclass", XRefRole("class"))
    app.connect("builder-inited", run_apidoc)
