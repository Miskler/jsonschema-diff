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

prop.compare_from_files(
    old_file_path="context.old.schema.json",
    new_file_path="context.new.schema.json"
)

prop.print(colorized=True, with_legend=False)
