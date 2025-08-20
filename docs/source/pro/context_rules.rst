.. _context_rules:

Context Rules Page
==================

Tables
------

* **``PAIR_CONTEXT_RULES``** – undirected cliques (render one ⇒ render all).  
* **``CONTEXT_RULES``**     – directed dependencies (``A ⇒ [B, C]``).

Resolution algorithm
--------------------

:py:meth:`RenderContextHandler.resolve` walks the primary render list, extending it with
dependencies while guaranteeing **stable order** and **single inclusion**.
