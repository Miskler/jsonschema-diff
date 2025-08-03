from jsonschema_diff.compare import property
from jsonschema_diff.config import config
from json import loads
from pprint import pprint

prop = property.Property(
    config=config,
    name="name",
    schema_path=[],
    json_path=[],
    old_schema=loads(open("old.schema.json").read()),
    new_schema=loads(open("new.schema.json").read()))

prop.compare()

result = prop.render()

print("\n\n\n".join(result))
