from jsonschema_diff import JsonSchemaDiff, ConfigMaker
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter

from jsonschema_diff.core.custom_compare import CompareList, CompareRange
from jsonschema_diff.core import Compare


prop = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline([
        MonoLinesHighlighter(),
        ReplaceGenericHighlighter(),
        PathHighlighter(),
    ])
)

print(prop.legend([Compare, CompareList, CompareRange]))
