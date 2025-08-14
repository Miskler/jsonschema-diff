from jsonschema_diff.core import Config, Property, Statuses


# ------------------------------------------------------------
# Вспомогательный конструктор
# ------------------------------------------------------------
def make_prop(
    old: dict | None,
    new: dict | None,
    *,
    name: str | int = "field",
    schema_path: list = None,
    json_path: list = None,
) -> Property:
    p = Property(
        config=Config(),
        name=name,
        schema_path=[] if schema_path is None else schema_path,
        json_path=[] if json_path is None else json_path,
        old_schema=old,
        new_schema=new,
    )
    p.compare()
    return p


# =================================================================
#                             Т Е С Т Ы
# =================================================================
# ---------- _get_keys ------------------------------------------------------
def test_get_keys_deterministic_order():
    p = make_prop({}, {})
    keys = p._get_keys({"a": 1, "b": 2}, {"b": 3, "c": 4})
    assert keys == ["a", "b", "c"]


# ---------- Примитивные статусы -------------------------------------------
def test_status_added_and_render():
    prop = make_prop({}, {"type": "string"})
    assert prop.status is Statuses.ADDED and prop.is_for_rendering()

    lines, _ = prop.render()
    # первая строка начинается с «+»
    assert lines[0].lstrip().startswith("+")
    # присутствует путь к полю и сама строка «string»
    assert '"field"]:' in lines[0] and "string" in lines[0]


def test_status_deleted():
    prop = make_prop({"enum": [1, 2]}, {})
    assert prop.status is Statuses.DELETED

    lines, _ = prop.render()
    assert lines[0].lstrip().startswith("-") and "[1, 2]" in lines[0]


def test_status_no_diff():
    sch = {"const": 42}
    prop = make_prop(sch, sch)
    assert prop.status is Statuses.NO_DIFF
    # NO_DIFF не выводится
    lines, _ = prop.render()
    assert lines == []


# ---------- MODIFIED: изменение простого параметра -------------------------
def test_status_modified_simple_param():
    prop = make_prop({"type": "string"}, {"type": "number"})
    assert prop.status is Statuses.MODIFIED
    # параметр «type» присутствует и имеет статус REPLACED
    tp = prop.parameters["type"]
    assert tp.status is Statuses.REPLACED

    lines, _ = prop.render()
    # строка diff-а содержит "string -> number"
    assert any("string -> number" in l for l in lines)


# ---------- Рекурсивные «properties» ---------------------------------------
def test_nested_property_changes_bubble_down_only():
    old = {"properties": {"child": {"type": "string"}}}
    new = {"properties": {"child": {"type": "number"}}}
    root = make_prop(old, new, name="root")

    # корень — NO_DIFF, но дочерний узел MODIFIED
    assert root.status is Statuses.NO_DIFF
    child = root.propertys["child"]
    assert child.status is Statuses.MODIFIED

    lines, _ = root.render()
    # выводится только дифф дочернего параметра
    assert any("string -> number" in l for l in lines)
    # при этом нет строки самого корня
    assert not any(".root:" in l for l in lines)


# ---------- prefixItems / items (массивы) ----------------------------------
def test_items_indexed_children():
    old = {"prefixItems": [{"type": "string"}]}
    new = {"prefixItems": [{"type": "string"}, {"type": "number"}]}
    prop = make_prop(old, new)

    # дочерний индекс 1 добавлен
    idx1 = prop.propertys[1]
    assert idx1.status is Statuses.ADDED
    lines, _ = prop.render()
    # убедимся, что путь содержит индекс [1]
    assert any("[1]" in l for l in lines)
