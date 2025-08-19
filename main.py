from jsonschema_diff import JsonSchemaDiff, ConfigMaker
from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter

from jsonschema_diff.core.parameter_base import Compare


prop = JsonSchemaDiff(
    config=ConfigMaker.make(),
    colorize_pipeline=HighlighterPipeline([
        MonoLinesHighlighter(),
        ReplaceGenericHighlighter(),
        PathHighlighter(),
    ]),
    legend_ignore=[
        Compare
    ]
)

prop.compare(
    old_schema="context.old.schema.json",
    new_schema="context.new.schema.json"
)

prop.print(with_legend=True)
