Config Maker
============

``ConfigMaker`` assembles a :class:`jsonschema_diff.core.Config` with sensible
defaults.  Each switch enables a family of comparison rules.

.. code-block:: python

   from jsonschema_diff import ConfigMaker

   # Minimal default configuration
   config = ConfigMaker.make()

   # Fine tuned configuration
   config = ConfigMaker.make(
       tab_size=4,
       list_comparator=False,          # disable list diffing
       additional_compare_rules={str: CustomComparator},
   )

The resulting object is passed to :class:`jsonschema_diff.JsonSchemaDiff` or the
low level :class:`jsonschema_diff.core.Property` tree.

