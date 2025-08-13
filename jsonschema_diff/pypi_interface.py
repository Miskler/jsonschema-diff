from jsonschema_diff.core import Compare


class JsonSchemaDiff:
    def __init__(
        self,
        tab_size: int = 2,
        path_render_with_properies: bool = False,
        path_render_with_items: bool = False,
        list_comparator: bool = True,
        
        range_digit_comparator: bool = True,
        range_length_comparator: bool = True,
        range_items_comparator: bool = True,
        range_properties_comparator: bool = True,

        additional_compare_rules: dict[str | type, Compare] = {},
        additional_combine_rules: list[list[str]] = [],
        additional_pair_context_rules: list[list[str | Compare]] = [],
        additional_context_rules: dict[str | Compare, list[str | Compare]] = {},
    ):
        ... 
