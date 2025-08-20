"""
Built-in high-lighter stages
============================

This *sub-package* bundles three ready-to-use implementations of
:class:`jsonschema_diff.color.abstraction.LineHighlighter` that cover the most
common needs when rendering a JSON-Schema diff to the terminal:

* :class:`MonoLinesHighlighter` – apply a foreground colour chosen from a
  *prefix → colour* mapping
* :class:`ReplaceGenericHighlighter` – highlight token-level changes within
  ``OLD -> NEW`` tails
* :class:`PathHighlighter` – pretty-print JSON-Pointer-like paths

Importing the package directly re-exports these classes so you can write
succinct code such as ::

    from jsonschema_diff.color.stages import MonoLinesHighlighter

Only the three public classes below are exported via :py:data:`__all__`.
"""

from .mono_lines import MonoLinesHighlighter
from .path import PathHighlighter
from .replace import ReplaceGenericHighlighter

__all__: list[str] = [
    "MonoLinesHighlighter",
    "ReplaceGenericHighlighter",
    "PathHighlighter",
]
