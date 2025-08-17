Combine rules
=============

Certain keywords are easier to read when grouped together.  ``combine_rules``
declare such sets.  When any key from the set changes, the others are shown in
the same table block.

.. code-block:: python

   config = ConfigMaker.make(
       additional_combine_rules=[
           ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"],
       ]
   )

Combine rules work alongside ``compare_rules`` – each key still needs a
comparator to describe the difference.

