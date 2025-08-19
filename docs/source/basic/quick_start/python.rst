.. _python_quick_start:
Python Interface
================

Чтобы быстро сравнить схемы и вывести результат в консоль:

.. code-block:: python

    from jsonschema_diff import JsonSchemaDiff, ConfigMaker
    from jsonschema_diff.color import HighlighterPipeline
    from jsonschema_diff.color.stages import (
        MonoLinesHighlighter, PathHighlighter, ReplaceGenericHighlighter,
    )

    prop = JsonSchemaDiff(
        config=ConfigMaker.make(),
        colorize_pipeline=HighlighterPipeline([
            MonoLinesHighlighter(),
            ReplaceGenericHighlighter(),
            PathHighlighter(),
        ])
    )

    prop.compare( # Фукция принимает как путь до файла, так и сами dict схемы // можно комбинировать
        old_schema="context.old.schema.json",
        new_schema="context.new.schema.json"
    )

    # Теперь можно вывести
    prop.print(with_legend=True)


