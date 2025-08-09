from jsonschema_diff.core import property
from jsonschema_diff.core.config import config
from json import loads
from pprint import pprint
from jsonschema_diff.color.stages.mono_lines import MonoLinesHighlighter
from jsonschema_diff.color.stages.replace import ReplaceGenericHighlighter
from jsonschema_diff.color.stages.path import PathHighlighter
from jsonschema_diff.color.base import HighlighterPipeline

prop = property.Property(
    config=config,
    name=None,
    schema_path=[],
    json_path=[],
    old_schema=loads(open("range.old.schema.json").read()),
    new_schema=loads(open("range.new.schema.json").read()))

prop.compare()

result = prop.render()

colored = HighlighterPipeline([
    MonoLinesHighlighter(),
    ReplaceGenericHighlighter(
        bg_color="grey30",
        underline_changes=False,
    ),
    PathHighlighter(),
]).colorize_lines("\n\n".join(result)) 

print(colored)

