from jsonschema_diff.combine import Combiner

from pprint import pprint

rules = [
    ["A", "B", "C"],   # группа 1
    ["A", "X", "Y"]         # группа 2
]

c = Combiner(rules, inner_key_field="field", inner_value_field="val")

subset = {
    "A": {"field": "color", "val": "red"},
    "C": {"field": "color", "val": "blue"},
    "B": {"field": "color", "val": "green"},
    "X": {"field": "color", "val": "white"},
    "Z": {"field": "color", "val": "yellow"},
}

pprint(c.combine(subset))
# {'color': ['red', 'blue', 'green']}

bad_subset = {
    "A": {"field": "color", "val": "red"},
    "C": {"field": "size",  "val": 42},
}
# -> ValueError: Правило требует один общий внутренний ключ, но обнаружены {'color', 'size'}

cross_group = {
    "A": {"field": "color", "val": "red"},
    "X": {"field": "color", "val": "white"},
}
# -> ValueError: Нельзя комбинировать ключи из разных групп