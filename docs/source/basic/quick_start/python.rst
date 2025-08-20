.. _python_quick_start:
Python Interface
================

To quickly compare schemas and print the result to the console:

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

    prop.compare( # Function accepts both file path and schema dict itself // can be combined
        old_schema="context.old.schema.json",
        new_schema="context.new.schema.json"
    )

    # Теперь можно вывести
    prop.print(with_legend=True)

.. jsonschemadiff:: basic/quick_start/jsons/example.old.schema.json basic/quick_start/jsons/example.new.schema.json
   :title: Terminal

See also for more: :mod:`jsonschema_diff.pypi_interface`
