"""
Convenience re-exports for the colour sub-package.

End-users can simply write::

    from jsonschema_diff.color import HighlighterPipeline, LineHighlighter
"""

from .abstraction import LineHighlighter
from .base import HighlighterPipeline

__all__ = ["HighlighterPipeline", "LineHighlighter"]
