Context rules
=============

Contextual information helps users understand why a keyword changed.  Two
collections control this behaviour:

``pair_context_rules``
   lists of related keys that should appear together (e.g. ``["type", "format"]``).

``context_rules``
   a mapping of a key to other keys that provide useful background when the first
   one changes.

.. code-block:: python

   config = ConfigMaker.make(
       additional_pair_context_rules=[["type", "format"]],
       additional_context_rules={"pattern": ["type"]},
   )

During rendering these rules add rows around the actual change, giving the reader
more context.

