.. _compare_rules:

Comparator Rules Page
=====================

Precedence tiers
----------------

#. ``(keyword, old_type, new_type)``  
#. ``keyword``  
#. ``(old_type, new_type)``  
#. ``old_type`` **or** ``new_type`` (single-sided)  
#. *default* comparator

Declaration
-----------

Add entries to ``Config.COMPARE_RULES``; resolution is performed by
:py:meth:`CompareRules.get_comparator`.

Extending
~~~~~~~~~

1. Implement a ``Compare`` subclass.  
2. Register it in the rules table.  
3. (Optional) expose it via ``ConfigMaker`` so convenience constructors pick it up.


Per-comparator options
----------------------

Some comparators support extra options via ``Config.COMPARE_CONFIG``.

Example: :py:class:`~jsonschema_diff.core.custom_compare.list.CompareList`
reads ``DICT_MATCH_THRESHOLD`` (default ``0.10``) to decide how strict
dict-to-dict matching inside arrays should be.

.. code-block:: python

   from jsonschema_diff.core import Config
   from jsonschema_diff.core.custom_compare import CompareList

   cfg = Config(
       compare_rules={
           list: CompareList,
       },
       compare_config={
           CompareList: {
               "DICT_MATCH_THRESHOLD": 0.25,
           },
       },
   )
