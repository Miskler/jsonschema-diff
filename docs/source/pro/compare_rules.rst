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
