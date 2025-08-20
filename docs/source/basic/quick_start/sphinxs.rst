.. _sphinx_quick_start:

Sphinx Extension
================

Use the extension in your build:

.. code-block:: python

    extensions += ["jsonschema_diff.sphinx"]

You must also configure the extension. Add the following variable to your `conf.py`:

.. code-block:: python

    from jsonschema_diff import ConfigMaker, JsonSchemaDiff
    from jsonschema_diff.color import HighlighterPipeline
    from jsonschema_diff.color.stages import (
        MonoLinesHighlighter, PathHighlighter, ReplaceGenericHighlighter,
    )

    jsonschema_diff = JsonSchemaDiff(
        config=ConfigMaker.make(),
        colorize_pipeline=HighlighterPipeline(
            [MonoLinesHighlighter(), ReplaceGenericHighlighter(), PathHighlighter()],
        ),
    )

After that, you can use it in your `.rst` files:

.. code-block:: rst

        .. jsonschemadiff:: path/to/file.old.schema.json path/to/file.new.schema.json # from folder `source`
            :name: filename.svg # optional
            :title: Title in virtual terminal # optional
            :no-legend: # optional

.. jsonschemadiff:: basic/quick_start/jsons/example.old.schema.json basic/quick_start/jsons/example.new.schema.json
   :title: Terminal
   :no-legend:

See also for more: :mod:`jsonschema_diff.sphinx.directive`
