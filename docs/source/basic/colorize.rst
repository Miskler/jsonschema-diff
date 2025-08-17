Colorize
========

Output can be ANSI colored by chaining :class:`jsonschema_diff.color.HighlighterPipeline`
stages.  The default pipeline applies three passes:

* ``MonoLinesHighlighter`` – reset style for each line.
* ``ReplaceGenericHighlighter`` – highlights additions/removals.
* ``PathHighlighter`` – emphasises JSON paths.

.. code-block:: python

   from jsonschema_diff.color import HighlighterPipeline
   from jsonschema_diff.color.stages import MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter

   pipeline = HighlighterPipeline([
       MonoLinesHighlighter(),
       ReplaceGenericHighlighter(),
       PathHighlighter(),
   ])

   diff = JsonSchemaDiff(config=ConfigMaker.make(), colorize_pipeline=pipeline)
   diff.compare_from_files("old.schema.json", "new.schema.json")
   diff.print(colorized=True)

Use ``--no-color`` in the CLI to suppress colors.

