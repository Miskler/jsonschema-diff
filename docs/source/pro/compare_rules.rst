Compare rules
=============

``compare_rules`` map JSON‑Schema keys to comparator classes.  When a key is
present in both old and new schemas, the associated comparator decides whether a
difference exists and how it should be displayed.

.. code-block:: python

   from jsonschema_diff import ConfigMaker
   from jsonschema_diff.core.custom_compare import CompareRange

   config = ConfigMaker.make(
       additional_compare_rules={"minimum": CompareRange}
   )

A comparator may also be registered for a Python ``type``.  For example the
built‑in :class:`~jsonschema_diff.core.custom_compare.CompareList` handles
``list`` values.

