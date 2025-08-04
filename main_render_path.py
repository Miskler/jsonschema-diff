from jsonschema_diff.path_render import PathRender

print(PathRender.render_path(
    ["properties", "name", "properties", "content", "items"],
    ["name", "content", 0]
))          # → ["name"]["content"].items[0]

print(PathRender.render_path(
    ["properties", "name", "properties", "content", "items"],
    ["name", "content"]
))          # → ["name"]["content"].items

print(PathRender.render_path(
    ["properties", "name", "properties", "content", "other"],
    ["name", "content", "other"]
))          # → ["name"]["content"]["other"]
