from typing import TypeAlias

from .custom_compare.list import CompareList
from .custom_compare.range import CompareRange
from .tools.combine import COMBINE_RULES_TYPE
from .tools.compare import COMPARE_RULES_TYPE
from .tools.context import CONTEXT_RULES_TYPE, PAIR_CONTEXT_RULES_TYPE
from .tools.render import PATH_MAKER_IGNORE_RULES_TYPE

COMPARE_CONFIG_TYPE: TypeAlias = dict[type, dict]

PROPERTY_KEY_GROUPS_TYPE: TypeAlias = dict[type, list[str]]


class Config:
    def __init__(
        self,
        tab: str = "  ",
        compare_rules: COMPARE_RULES_TYPE = {},
        combine_rules: COMBINE_RULES_TYPE = [],
        path_maker_ignore: PATH_MAKER_IGNORE_RULES_TYPE = ["properties", "items"],
        pair_context_rules: PAIR_CONTEXT_RULES_TYPE = [],
        context_rules: CONTEXT_RULES_TYPE = {},
        compare_config: COMPARE_CONFIG_TYPE = {},
        property_key_groups: PROPERTY_KEY_GROUPS_TYPE = {
            dict: ["properties", "$defs"],
            list: ["prefixItems", "items"],  # , "oneOf", "allOf", "anyOf"],
        },
    ):
        self.TAB: str = tab

        self.COMPARE_RULES: COMPARE_RULES_TYPE = compare_rules

        self.COMBINE_RULES: COMBINE_RULES_TYPE = combine_rules

        self.PATH_MAKER_IGNORE: PATH_MAKER_IGNORE_RULES_TYPE = path_maker_ignore

        self.PAIR_CONTEXT_RULES: PAIR_CONTEXT_RULES_TYPE = pair_context_rules
        self.CONTEXT_RULES: CONTEXT_RULES_TYPE = context_rules

        self.COMPARE_CONFIG: COMPARE_CONFIG_TYPE = compare_config
        """Configs for comparators.
        Can be obtained from Compare.my_config (content can be anything)"""

        self.PROPERTY_KEY_GROUPS: PROPERTY_KEY_GROUPS_TYPE = property_key_groups


default_config = Config(
    compare_rules={
        list: CompareList,
        #  ЧИСЛА
        "minimum": CompareRange,
        "maximum": CompareRange,
        "exclusiveMinimum": CompareRange,
        "exclusiveMaximum": CompareRange,
        #  СТРОКИ (длины)
        "minLength": CompareRange,
        "maxLength": CompareRange,
        #  МАССИВЫ (число элементов)
        "minItems": CompareRange,
        "maxItems": CompareRange,
        #  ОБЪЕКТЫ (число свойств)
        "minProperties": CompareRange,
        "maxProperties": CompareRange,
    },
    combine_rules=[
        ["minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum"],
        ["minLength", "maxLength"],
        ["minItems", "maxItems"],
        ["minProperties", "maxProperties"],
    ],
    pair_context_rules=[
        ["type", "format"],  # строковые форматы
        ["contentEncoding", "contentMediaType"],  # парные контент-атрибуты для строк
        ["if", "then", "else"],  # логический триплет показываем вместе
        ["properties", "required"],  # объект: список свойств и обязательность
        ["items", "prefixItems"],  # массив: позиционные/общие элементы
        ["contains", "minContains", "maxContains"],  # массив: contains и его пороги
        ["dependentRequired", "dependentSchemas"],  # объект: зависимости
        ["readOnly", "writeOnly"],  # метаданные доступа поля
        ["$ref", "$defs"],  # ссылка и её пространство имён
        [
            "additionalProperties",
            "unevaluatedProperties",
        ],  # политика для «прочих» свойств
        ["propertyNames", "patternProperties"],  # правила по именам vs по паттернам
        ["pattern", "format"],  # для строк часто полезно показать оба
    ],
    context_rules={
        # Строки
        "pattern": ["type"],  # есть паттерн — покажем, что это строка
        "contentMediaType": ["type", "contentEncoding"],
        "contentEncoding": ["type", "contentMediaType"],
        "contentSchema": ["type", "contentMediaType"],
        # Числа
        "multipleOf": ["type"],  # кратность имеет смысл для number/integer
        # Массивы
        "items": ["contains", "prefixItems", "uniqueItems", "unevaluatedItems"],
        "prefixItems": ["items", "unevaluatedItems"],
        "contains": ["minContains", "maxContains", "items"],
        "uniqueItems": ["type", "items"],
        # Объекты
        "properties": ["required", "additionalProperties", "patternProperties"],
        "required": ["properties"],  # дублирует пару, но безвредно
        "patternProperties": ["additionalProperties"],
        "dependentSchemas": ["dependentRequired", "properties"],
        "dependentRequired": ["properties"],
        "propertyNames": ["type"],
        # Комбинаторы
        "oneOf": ["type"],
        "anyOf": ["type"],
        "allOf": ["type"],
        "not": ["type"],
        # Референсы/мета
        "$ref": ["$defs"],
    },
)
