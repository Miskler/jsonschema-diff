CLI
===

A command line interface mirrors the Python API.

Basic invocation:

.. code-block:: console

   jsonschema-diff old.schema.json new.schema.json

Options:

.. code-block:: console

   jsonschema-diff --help

Use ``--no-color`` to disable ANSI colors, ``--no-legend`` to suppress the
legend table and ``--exit-code`` to return ``1`` when differences are found.

