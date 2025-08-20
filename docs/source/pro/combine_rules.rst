.. _combine_rules:

Combination Rules
=================

Purpose
-------

Some keywords only make sense as a unit (e.g. *minItems* and *maxItems*).  
`COMBINE_RULES` tells the engine to merge such keys into one
``CompareCombined`` instance so they are rendered together.

Rule format
-----------

*Outer list order* ⇒ screen order.  
*Inner list* ⇒ all keywords **must map to the same** ``Compare`` subclass or
``LogicCombinerHandler.combine`` raises ``ValueError``

Customising
~~~~~~~~~~~

.. code-block:: python

    cfg = ConfigMaker.make(
        additional_combine_rules=[["multipleOf", "divisibleBy"]],
        additional_compare_rules={"divisibleBy": CompareRange},
    )
