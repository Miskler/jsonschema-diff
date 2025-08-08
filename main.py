from jsonschema_diff import property
from jsonschema_diff.config import config
from json import loads
from pprint import pprint
from jsonschema_diff.color.mono import MonoHighlighter

prop = property.Property(
    config=config,
    name=None,
    schema_path=[],
    json_path=[],
    old_schema=loads(open("range.old.schema.json").read()),
    new_schema=loads(open("range.new.schema.json").read()))

prop.compare()

result = prop.render()

colored = MonoHighlighter().colorize_lines("\n\n".join(result))

print(colored)

