import pytest

# ------------------------------------------------------------
# Подготовка «заглушек» для Config и Statuses
# ------------------------------------------------------------
class DummyConfig:
    TAB = "··"          # две точки вместо пробела, чтобы легко увидеть

class DummyStatus:
    """Простейший контейнер с нужным атрибутом .value."""
    def __init__(self, value: str):
        self.value = value

STATUS_ADDED   = DummyStatus("+")
STATUS_REMOVED = DummyStatus("-")


# ------------------------------------------------------------
# Тестируемый объект
# ------------------------------------------------------------
from jsonschema_diff.core.tools import RenderTool


# ------------------------------------------------------------
# make_tab / make_prefix
# ------------------------------------------------------------
def test_make_tab_multiplies_tab_symbol():
    assert RenderTool.make_tab(DummyConfig, 3) == DummyConfig.TAB * 3


@pytest.mark.parametrize("status, expected", [(STATUS_ADDED, "+"), (STATUS_REMOVED, "-")])
def test_make_prefix_returns_value(status, expected):
    assert RenderTool.make_prefix(status) == expected


# ------------------------------------------------------------
# make_path – «Золотой» happy-path
# ------------------------------------------------------------
def test_make_path_full_match():
    schema = ["root", "items", 0, "name"]
    json   = ["root", "items", 0, "name"]
    result = RenderTool.make_path(schema, json)
    assert result == '["root"]["items"][0]["name"]'


# ------------------------------------------------------------
# Игнорирование схемных служебных токенов
# ------------------------------------------------------------
def test_make_path_ignores_default_properties_tokens():
    schema = ["properties", "user", "properties", "age"]
    json   = ["user", "age"]
    result = RenderTool.make_path(schema, json)
    assert result == '["user"]["age"]'


def test_make_path_ignores_custom_tokens():
    schema = ["definitions", "node"]
    json   = ["node"]
    result = RenderTool.make_path(schema, json, ignore=("definitions",))
    assert result == '["node"]'


# ------------------------------------------------------------
# «Схема-только» токены → .key
# ------------------------------------------------------------
def test_make_path_schema_only_tokens_prefixed_with_dot():
    schema = ["allOf", "0", "properties", "user"]
    json   = ["user"]
    result = RenderTool.make_path(schema, json)
    # 'allOf' и '0' (строка-цифра) должны пойти как .allOf.0
    assert result == '.allOf.0["user"]'


# ------------------------------------------------------------
# «Хвост» json_path после окончания schema_path
# ------------------------------------------------------------
def test_make_path_appends_remaining_json_tail():
    schema = ["user"]
    json   = ["user", "address", "street"]
    result = RenderTool.make_path(schema, json)
    assert result == '["user"]["address"]["street"]'


# ------------------------------------------------------------
# Числовые токены выводятся без кавычек
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "idx_token, expected",
    [
        (3, '["items"][3]["name"]'),   # int
        ("3", '["items"]["3"]["name"]')  # строка-цифра остаётся в кавычках
    ],
)
def test_make_path_numeric_token_formats(idx_token, expected):
    schema = ["items", idx_token, "name"]
    json   = ["items", idx_token, "name"]
    assert RenderTool.make_path(schema, json) == expected


# ------------------------------------------------------------
# Пограничные случаи
# ------------------------------------------------------------
def test_make_path_with_empty_schema():
    assert RenderTool.make_path([], ["foo"]) == '["foo"]'


def test_make_path_with_empty_json():
    assert RenderTool.make_path(["metadata"], []) == ".metadata"
