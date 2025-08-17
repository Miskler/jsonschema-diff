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
]

autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns: list[str] = []


# -- HTML output -------------------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]


# -- Dynamic documentation builders -----------------------------------------


def generate_examples(app: "Sphinx") -> None:
    """Create ``basic/real_world_examples.rst`` from schema pairs."""
    root = Path(app.confdir).resolve().parent.parent
    target = Path(app.confdir) / "basic" / "real_world_examples.rst"

    config = ConfigMaker.make()
    pipeline = HighlighterPipeline(
        [MonoLinesHighlighter(), ReplaceGenericHighlighter(), PathHighlighter()]
    )

    lines = [
        "Real-world Examples",
        "===================",
        "",
        "Generated from ``*.old.schema.json`` / ``*.new.schema.json`` pairs.",
        "",
    ]

    for old_file in sorted(root.glob("*.old.schema.json")):
        base = old_file.name.replace(".old.schema.json", "")
        new_file = root / old_file.name.replace("old.schema.json", "new.schema.json")
        if not new_file.exists():
            continue
        label = base or "example"
        with open(old_file, "r", encoding="utf-8") as f_old, open(
            new_file, "r", encoding="utf-8"
        ) as f_new:
            rendered, _ = JsonSchemaDiff.fast_pipeline(
                config, json.load(f_old), json.load(f_new), pipeline
            )
        lines.append(label)
        lines.append("-" * len(label))
        lines.append("")
        lines.append("::")
        lines.append("")
        lines.extend([f"   {line}" for line in rendered.splitlines()])
        lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")


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
    app.connect("builder-inited", generate_examples)
    app.connect("builder-inited", run_apidoc)
