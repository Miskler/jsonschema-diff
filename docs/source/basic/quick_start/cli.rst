.. _cli_quick_start:
CLI
===

A command line interface mirrors the Python API.

Basic invocation:

.. code-block:: console

   jsonschema-diff old.schema.json new.schema.json

.. jsonschemadiff:: basic/quick_start/jsons/example.old.schema.json basic/quick_start/jsons/example.new.schema.json
   :title: Terminal
   :no-legend:

OR

.. code-block:: console

   jsonschema-diff "{\"type\":\"string\"}" "{\"type\":\"number\"}" # escaping is required

.. jsonschemadiff:: basic/quick_start/jsons/type.old.schema.json basic/quick_start/jsons/type.new.schema.json
   :title: Terminal
   :no-legend:

Options:

.. code-block:: console

   jsonschema-diff --help

* ``--no-color`` to disable ANSI colors.
* ``--legend`` to show legend table.
* ``--exit-code`` to return ``1`` when differences are found.

See also for more: :mod:`jsonschema_diff.cli`
