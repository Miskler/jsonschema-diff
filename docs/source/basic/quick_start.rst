Quick Start
===========

Install the library and compare two schemas in a few lines.

.. code-block:: console

   pip install jsonschema-diff

.. code-block:: python

   from jsonschema_diff import ConfigMaker, JsonSchemaDiff
   from jsonschema_diff.color import HighlighterPipeline
   from jsonschema_diff.color.stages import MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter
   from jsonschema_diff.core.parameter_base import Compare

   diff = JsonSchemaDiff(
       config=ConfigMaker.make(),
       colorize_pipeline=HighlighterPipeline([
           MonoLinesHighlighter(),
           ReplaceGenericHighlighter(),
           PathHighlighter(),
       ]),
       legend_ignore=[Compare],
   )
   diff.compare_from_files("old.schema.json", "new.schema.json")
   print(diff.render(colorized=False))

Alternatively, use the CLI:

.. code-block:: console

   jsonschema-diff old.schema.json new.schema.json

