from jsonschema_diff.core import Compare
from jsonschema_diff.color import HighlighterPipeline
from typing import Iterable, Optional


class JsonSchemaDiff:
    def __init__(
        self,
        config: "Config",
        colorize_pipeline: Optional["HighlighterPipeline"] = None
    ):
        ... 
