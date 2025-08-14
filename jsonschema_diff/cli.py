#!/usr/bin/env python3
"""
Diff two JSON-Schema files directly from the terminal.

Examples
--------
$ jsonschema-diff old.schema.json new.schema.json
"""

from __future__ import annotations

import argparse
import sys

from jsonschema_diff import ConfigMaker, JsonSchemaDiff
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter,
    PathHighlighter,
    ReplaceGenericHighlighter,
)
from jsonschema_diff.core.parameter_base import Compare


def _make_highlighter(disable_color: bool) -> HighlighterPipeline:
    """
    Return an empty ``HighlighterPipeline`` if *disable_color* is ``True``,
    otherwise the default 3-stage pipeline.

    Parameters
    ----------
    disable_color : bool
        When ``True`` ANSI colors are suppressed even if the terminal supports them.
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
    """Build and return the CLI argument parser."""
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
        "--no-legend",
        action="store_true",
        help="Do not print the legend at the end",
    )
    p.add_argument(
        "--no-body",
        action="store_true",
        help="Print only the legend (if not suppressed) but skip the diff body",
    )

    # Exit-code control
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Return 1 if differences are detected, otherwise 0",
    )

    return p


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    """Entry-point used by ``__main__`` and the console script."""
    args = _build_parser().parse_args(argv)

    # 1. Build the wrapper object
    diff = JsonSchemaDiff(
        config=ConfigMaker.make(),
        colorize_pipeline=_make_highlighter(args.no_color),
        legend_ignore=[Compare],  # as in the library example
    )

    # 2. Compare the files
    diff.compare_from_files(
        old_file_path=args.old_schema,
        new_file_path=args.new_schema,
    )

    # 3. Print the result
    diff.print(
        colorized=not args.no_color,
        with_body=not args.no_body,
        with_legend=not args.no_legend,
    )

    # 4. Optional special exit code
    if args.exit_code:
        # ``last_compare_list`` is filled during render/print.
        sys.exit(1 if diff.last_compare_list else 0)


if __name__ == "__main__":  # pragma: no cover
    main()
