from jsonschema_diff.core import property
from jsonschema_diff.core.config import default_config
from json import loads

from jsonschema_diff.color import HighlighterPipeline
from jsonschema_diff.color.stages import MonoLinesHighlighter, ReplaceGenericHighlighter, PathHighlighter

prop = property.Property(
    config=default_config,
    name=None,
    schema_path=[],
    json_path=[],
    old_schema=loads(open("context.old.schema.json").read()),
    new_schema=loads(open("context.new.schema.json").read()))

prop.compare()

result = prop.render()

colored = HighlighterPipeline([
    MonoLinesHighlighter(),
    ReplaceGenericHighlighter(),
    PathHighlighter(),
]).colorize_lines("\n\n".join(result)) 

print(colored)

