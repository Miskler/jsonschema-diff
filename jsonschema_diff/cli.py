#!/usr/bin/env python3
"""
Diff two JSON-Schema files right from the terminal.

$ jsonschema-diff context.old.schema.json context.new.schema.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema_diff import JsonSchemaDiff, ConfigMaker
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import (
    MonoLinesHighlighter,
    ReplaceGenericHighlighter,
    PathHighlighter,
)
from jsonschema_diff.core.parameter_base import Compare


def _make_highlighter(disable_color: bool) -> HighlighterPipeline:
    """
    Вернёт «пустой» pipeline, если цвета запрещены,
    иначе — стандартный набор из трёх стадий.
    """
    if disable_color:  # user passed --no-color
        return HighlighterPipeline([])
    return HighlighterPipeline(
        [
            MonoLinesHighlighter(),
            ReplaceGenericHighlighter(),
            PathHighlighter(),
        ]
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="jsonschema-diff",
        description="Показывает разницу между двумя JSON-Schema",
    )

    p.add_argument("old_schema", help="Путь к «старой» схеме")
    p.add_argument("new_schema", help="Путь к «новой» схеме")

    # вывод
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Отключить ANSI-цвета даже, если терминал их поддерживает",
    )
    p.add_argument(
        "--no-legend",
        action="store_true",
        help="Не выводить легенду в конце",
    )
    p.add_argument(
        "--no-body",
        action="store_true",
        help="Не выводить сам diff, а только легенду (если не отключена)",
    )

    # управление кодом возврата
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Вернуть код 1, если обнаружены отличия, иначе 0",
    )

    return p


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = _build_parser().parse_args(argv)

    # 1. Конструируем объект-обёртку
    diff = JsonSchemaDiff(
        config=ConfigMaker.make(),
        colorize_pipeline=_make_highlighter(args.no_color),
        legend_ignore=[Compare],  # как в вашем примере
    )

    # 2. Запускаем сравнение файлов
    diff.compare_from_files(
        old_file_path=args.old_schema,
        new_file_path=args.new_schema,
    )

    # 3. Печатаем
    diff.print(
        colorized=not args.no_color,
        with_body=not args.no_body,
        with_legend=not args.no_legend,
    )

    # 4. Нужен ли особый код возврата?
    if args.exit_code:
        # last_compare_list заполняется при render/print :contentReference[oaicite:0]{index=0}.
        # Если список пуст, отличий нет.
        sys.exit(1 if diff.last_compare_list else 0)


if __name__ == "__main__":  # pragma: no cover
    main()
