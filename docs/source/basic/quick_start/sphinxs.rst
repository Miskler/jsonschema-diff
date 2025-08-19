.. _sphinx_quick_start:
Sphinx Extension
================

Применяем расширение в нашу сборку:

.. code-block:: python

    extensions += ["jsonschema_diff.sphinx"]

Так же обязательно нужно сконфигурировать его. Добавьте в `conf.py` следующую переменную:

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

После вы можете использовать его в своих `.rst` файлах:

.. code-block:: rst

        .. jsonschemadiff:: path/to/file.old.schema.json path/to/file.new.schema.json
            :name: filename.svg # optional
            :title: Title in virtual terminal # optional
            :no-legend: # optional


