"""
jsonschema_diff CLI
===================

A tiny command-line front-end around :py:mod:`jsonschema_diff`
that highlights semantic differences between two JSON-Schema
documents directly in your terminal.

Typical usage
-------------
>>> jsonschema-diff old.schema.json new.schema.json
>>> jsonschema-diff --no-color --legend old.json new.json
>>> jsonschema-diff --exit-code old.json new.json  # useful in CI

Exit status
-----------
* **0** – the two schemas are semantically identical
* **1** – at least one difference was detected (only when
  ``--exit-code`` is given)

The CLI is intentionally minimal: *all* comparison options are taken
from :pyclass:`jsonschema_diff.ConfigMaker`, so the behaviour stays
in sync with the library defaults.

"""

from __future__ import annotations

import argparse
import json
import sys

from jsonschema_diff import ConfigMaker, JsonSchemaDiff
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter,
    PathHighlighter,
    ReplaceGenericHighlighter,
)
from jsonschema_diff.core.compare_base import Compare


def _make_highlighter(disable_color: bool) -> HighlighterPipeline:
    """
    Create the high-lighting pipeline used to colorise diff output.

    Parameters
    ----------
    disable_color :
        When *True* ANSI escape sequences are suppressed even if the
        invoking TTY advertises color support (e.g. when piping the
        output into a file).

    Returns
    -------
    HighlighterPipeline
        Either an **empty** pipeline (no colour) or the standard
        three-stage pipeline consisting of
        :class:`~jsonschema_diff.color.stages.MonoLinesHighlighter`,
        :class:`~jsonschema_diff.color.stages.ReplaceGenericHighlighter`
        and :class:`~jsonschema_diff.color.stages.PathHighlighter`.

    Note
    -----
    The composition of the *default* pipeline mirrors what the core
    library exposes; duplicating the stages here keeps the CLI fully
    self-contained while allowing future customisation.

    Examples
    --------
    >>> _make_highlighter(True)
    HighlighterPipeline(stages=[])
    >>> _make_highlighter(False).stages   # doctest: +ELLIPSIS
    [<jsonschema_diff.color.stages.MonoLinesHighlighter ...>, ...]
    """
    if disable_color:
        return HighlighterPipeline([])
    return HighlighterPipeline(
        [
            MonoLinesHighlighter(),
            ReplaceGenericHighlighter(),
            PathHighlighter(),
        ]
    )


def _build_parser() -> argparse.ArgumentParser:
    """
    Construct the :pyclass:`argparse.ArgumentParser` for the CLI.

    Returns
    -------
    argparse.ArgumentParser
        The fully configured parser containing positional arguments
        for the *old* and *new* schema paths, together with three
        optional feature flags.

    See Also
    --------
    * :pyfunc:`main` – where the parser is consumed.
    * The *argparse* documentation for available formatting options.
    """
    p = argparse.ArgumentParser(
        prog="jsonschema-diff",
        description="Show the difference between two JSON-Schema files",
    )

    # Positional arguments
    p.add_argument("old_schema", help="Path to the *old* schema")
    p.add_argument("new_schema", help="Path to the *new* schema")

    # Output options
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors even if the terminal supports them",
    )
    p.add_argument(
        "--legend",
        action="store_true",
        help="Print a legend explaining diff symbols at the end",
    )

    # Exit-code control
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Return **1** if differences are detected, otherwise **0**",
    )

    return p


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    """
    CLI entry-point (invoked by ``python -m jsonschema_diff`` or by the
    ``jsonschema-diff`` console script).

    Parameters
    ----------
    argv :
        Command-line argument vector **excluding** the executable name.
        When *None* (default) ``sys.argv[1:]`` is used – this is the
        behaviour required by *setuptools* console-scripts.


    Note
    ----
        The function performs four sequential steps:

        1. Build a :class:`JsonSchemaDiff` instance.
        2. Compare the two user-supplied schema files.
        3. Print a colourised diff (optionally with a legend).
        4. Optionally exit with code 1 if differences are present.

    """
    args = _build_parser().parse_args(argv)

    # 1. Build the wrapper object
    diff = JsonSchemaDiff(
        config=ConfigMaker.make(),
        colorize_pipeline=_make_highlighter(args.no_color),
        legend_ignore=[Compare],  # as in the library example
    )

    def try_load(data: str) -> dict | str:
        try:
            return dict(json.loads(data))
        except json.JSONDecodeError:
            return str(data)

    # 2. Compare the files
    diff.compare(
        old_schema=try_load(args.old_schema),
        new_schema=try_load(args.new_schema),
    )

    # 3. Print the result
    diff.print(
        with_legend=args.legend,
    )

    # 4. Optional special exit code
    if args.exit_code:
        # ``last_compare_list`` is filled during render/print.
        sys.exit(1 if diff.last_compare_list else 0)


if __name__ == "__main__":  # pragma: no cover
    main()
