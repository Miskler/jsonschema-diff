Colorize
========

Output can be ANSI colored by chaining :class:`~jsonschema_diff.color.HighlighterPipeline`
stages.  The default pipeline applies three passes:

* :class:`~jsonschema_diff.color.stages.MonoLinesHighlighter` – mono color line by prefix (`+` `-` `r` `m`).
* :class:`~jsonschema_diff.color.stages.ReplaceGenericHighlighter` – highlights additions/removals in `r` lines.
* :class:`~jsonschema_diff.color.stages.PathHighlighter` – emphasises JSON paths.

.. code-block:: python

    from jsonschema_diff.color import HighlighterPipeline
    from jsonschema_diff.color.stages import (
        MonoLinesHighlighter, PathHighlighter, ReplaceGenericHighlighter,
    )

    pipeline = HighlighterPipeline([
        MonoLinesHighlighter(),
        ReplaceGenericHighlighter(),
        PathHighlighter(),
    ])

    diff = JsonSchemaDiff(config=ConfigMaker.make(), colorize_pipeline=pipeline)
    diff.compare_from_files("old.schema.json", "new.schema.json")
    diff.print(colorized=True)

Use empty list to disable colorization:

.. code-block:: python

    pipeline = HighlighterPipeline([])
