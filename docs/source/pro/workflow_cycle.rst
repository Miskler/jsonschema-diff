.. _workflow_cycle_overview:

Workflow Cycle Overview
=======================

This architectural primer shows **what flows where — and why** when two JSON Schemas are
compared.  The *mechanics* of rule look-ups live in the dedicated pages linked below; here
we stay on the high-level picture.


Prerequisites fixed since the previous draft
--------------------------------------------

.. note::

   * Helper names aligned (e.g. colour pipeline via
     ``JsonSchemaDiff.fast_pipeline``).
   * Legacy container ``propertys`` renamed to ``children``.
   * All intra-library references point to real public symbols.

1. Entry Point & Inputs
-----------------------

.. code-block:: python

   JsonSchemaDiff(...).compare(old_schema, new_schema).print()

* **``old_schema`` / ``new_schema``** – *dict* objects or paths to ``.json`` files.  
* **``Config``** – bundles *compare*, *combine* and *context* tables plus render flags.  
* *Optional* **``HighlighterPipeline``** – post-processing ANSI colouriser.


2. Building the *Property* tree
-------------------------------

Each call to :py:meth:`Property.compare` spawns a recursive walk that mirrors the shape of
the input schemas.  Leaf keywords become ``Compare`` instances, nested structures create
child ``Property`` nodes.


3. Comparator Selection (overview)
----------------------------------

The resolver in ``compare.py`` applies **five fallback tiers** to pick the most specific
``Compare`` subclass for a *(keyword, old_type, new_type)* combination (key-specific →
key-agnostic).

*Detailed table syntax*: see :doc:`compare_rules`.


4. Logical Combination of Parameters
------------------------------------

Some keywords form semantic pairs (*minItems* + *maxItems*, *pattern* + *format*, …).  The
handler in ``combine.py`` merges such groups into synthetic ``CompareCombined`` objects so
that range logic works on both values at once.

.. code-block:: python

   COMBINE_RULES = [
       ["minItems", "maxItems"],
       ["minimum",  "maximum"],
       # … more groups …
   ]

*Syntactic details*: :doc:`combine_rules`.


5. Context Expansion
--------------------

Before anything is printed, the engine resolves **what must be shown**.  Two tables guide
the process:

* ``PAIR_CONTEXT_RULES`` – undirected → «render one ⇒ render all».  
* ``CONTEXT_RULES``     – directed    → «A ⇒ [B, C]».

The algorithm walks the initial render list, pulling additional comparators until the
dependency graph is closed.

.. code-block:: python

   CONTEXT_RULES = {
       ChangedType : [RemovedKeyword, AddedKeyword],
       CompareRange: [ChangedNumber],
   }

*Directive formats*: :doc:`context_rules`.


6. Rendering
------------

* :py:meth:`RenderTool.make_path` converts internal coordinate tuples to a concise string
  like ``["items"][0].additionalProperties``.
* Tabs & prefixes are added, then the body may be piped through a colouriser.
* :py:meth:`JsonSchemaDiff.legend` appends a one-line glossary of comparator classes used.


7. Call Timeline (cheat sheet)
------------------------------

.. code-block:: text

   User code
       ↓ compare()
   JsonSchemaDiff
       ↓ Property.compare()         — recursion & raw param list
   CompareRules                     — choose Compare classes
   LogicCombinerHandler             — merge keyword groups
   RenderContextHandler             — expand context set
   RenderTool                       — build printable paths
   JsonSchemaDiff.render()          — join + colourise and return
   JsonSchemaDiff.print()           — print to stdout
