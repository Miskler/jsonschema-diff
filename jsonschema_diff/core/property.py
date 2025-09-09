from typing import TYPE_CHECKING

from .abstraction import Statuses, ToCompare
from .compare_base import Compare
from .tools import CompareRules, LogicCombinerHandler, RenderContextHandler
from .tools import RenderTool as RT

if TYPE_CHECKING:
    from .config import Config


class Property:
    def __init__(
        self,
        config: "Config",
        schema_path: list[str | int],
        json_path: list[str | int],
        name: str | int | None,
        old_schema: dict | None,
        new_schema: dict | None,
    ):
        self.status: Statuses = Statuses.UNKNOWN
        self.parameters: dict[str, "Compare"] = {}
        self.propertys: dict[str | int, "Property"] = {}

        self.config = config
        self.name = name
        self.schema_path = schema_path
        self.json_path = json_path

        self.old_schema = {} if old_schema is None else old_schema
        self.new_schema = {} if new_schema is None else new_schema

    @property
    def json_path_with_name(self) -> list[str | int]:
        json_path_with_name = self.json_path
        if self.name is not None:
            json_path_with_name = self.json_path + [self.name]

        return json_path_with_name

    @property
    def schema_path_with_name(self) -> list[str | int]:
        schema_path_with_name = self.schema_path
        if self.name is not None:
            schema_path_with_name = self.schema_path + [self.name]

        return schema_path_with_name

    def _get_keys(self, old: dict | None, new: dict | None) -> list[str]:
        """
        Детерминированное объединение ключей:
        1) все ключи из old в их исходном порядке;
        2) затем ключи из new, которых не было в old, в их порядке.
        """
        old_keys = list(old.keys()) if isinstance(old, dict) else []
        new_keys = list(new.keys()) if isinstance(new, dict) else []
        seen = set()
        merged = []
        for k in old_keys:
            if k not in seen:
                merged.append(k)
                seen.add(k)
        for k in new_keys:
            if k not in seen:
                merged.append(k)
                seen.add(k)
        return merged

    def compare(self) -> None:
        if len(self.old_schema) <= 0 and len(self.new_schema) > 0:
            self.status = Statuses.ADDED
        elif len(self.new_schema) <= 0:  # безопасное разрешение конфликта когда пара пустая
            self.status = Statuses.DELETED

        parameters_subset = {}
        keys = self._get_keys(self.old_schema, self.new_schema)
        for key in keys:
            old_key = key if key in self.old_schema else None
            old_value = self.old_schema.get(key, None)

            new_key = key if key in self.new_schema else None
            new_value = self.new_schema.get(key, None)

            if key in self.config.PROPERTY_KEY_GROUPS[dict]:  # словари содержащие Property
                prop_keys = self._get_keys(old_value, new_value)
                for prop_key in prop_keys:
                    old_to_prop = None if old_value is None else old_value.get(prop_key, None)
                    new_to_prop = None if new_value is None else new_value.get(prop_key, None)

                    prop = Property(
                        config=self.config,
                        schema_path=self.schema_path_with_name + [key],
                        json_path=self.json_path_with_name,
                        name=prop_key,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop,
                    )
                    prop.compare()
                    self.propertys[prop_key] = prop
            elif key in self.config.PROPERTY_KEY_GROUPS[list]:  # массивы содержащие Property
                if not isinstance(old_value, list):
                    old_value = [old_value]
                old_len = len(old_value)
                if not isinstance(new_value, list):
                    new_value = [new_value]
                new_len = len(new_value)

                for i in range(max(new_len, old_len)):
                    old_to_prop = None if i >= old_len else old_value[i]
                    new_to_prop = None if i >= new_len else new_value[i]

                    prop = Property(
                        config=self.config,
                        schema_path=self.schema_path_with_name + [key],
                        json_path=self.json_path_with_name,
                        name=i,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop,
                    )
                    prop.compare()
                    self.propertys[i] = prop
            else:
                parameters_subset[key] = {
                    "comparator": CompareRules.get_comparator_from_values(
                        rules=self.config.COMPARE_RULES,
                        default=Compare,
                        key=key,
                        old=old_value,
                        new=new_value,
                    ),
                    "to_compare": ToCompare(
                        old_key=old_key,
                        old_value=old_value,
                        new_key=new_key,
                        new_value=new_value,
                    ),
                }

        result_combine = LogicCombinerHandler.combine(
            subset=parameters_subset,
            rules=self.config.COMBINE_RULES,
            inner_key_field="comparator",
            inner_value_field="to_compare",
        )

        for values in result_combine.values():
            comparator_cls = values["comparator"]
            comparator = comparator_cls(
                self.config,
                self.schema_path_with_name,
                self.json_path_with_name,
                values["to_compare"],
            )

            comparator.compare()

            if comparator.is_for_rendering() and self.status == Statuses.UNKNOWN:
                self.status = Statuses.MODIFIED

            self.parameters[comparator.get_name()] = comparator

        if self.status == Statuses.UNKNOWN:
            self.status = Statuses.NO_DIFF

    def is_for_rendering(self) -> bool:
        return self.status in [
            Statuses.ADDED,
            Statuses.DELETED,
            Statuses.REPLACED,
            Statuses.MODIFIED,
        ]

    def calc_diff(self) -> dict[str, int]:
        """
        Summarizes the difference statistics:
        - all parameters (Compare.calc_diff)
        - child properties (Property.calc_diff)
        - plus the status of the current Property (as a single observation)
        """
        stats: dict[str, int] = {
            "ADDED": 0,
            "DELETED": 0,
            "REPLACED": 0,
            "MODIFIED": 0,
            "NO_DIFF": 0,
            "UNKNOWN": 0,
        }
        # current Property status
        stats[self.status.name] += 1

        def _merge_stats(dst: dict[str, int], src: dict[str, int]) -> None:
            for key, value in src.items():
                dst[key] = dst.get(key, 0) + value

        # parameters (Compare)
        for cmp in self.parameters.values():
            _merge_stats(stats, cmp.calc_diff())

        # child properties
        for prop in self.propertys.values():
            _merge_stats(stats, prop.calc_diff())

        return stats

    def get_for_rendering(self) -> list["Compare"]:
        # Определение что рендерить
        not_for_render = {}
        for_render = {}
        for param_name, param in self.parameters.items():
            if param.is_for_rendering():
                for_render[param_name] = param
            else:
                not_for_render[param_name] = param

        with_context = RenderContextHandler.resolve(
            pair_context_rules=self.config.PAIR_CONTEXT_RULES,
            context_rules=self.config.CONTEXT_RULES,
            for_render=for_render,
            not_for_render=not_for_render,
        )

        return list(with_context.values())

    def self_render(
        self, tab_level: int = 0, all_for_rendering: bool = False
    ) -> tuple[str, list[type["Compare"]]]:
        # Определение что рендерить
        to_render_count = (
            self.get_for_rendering() if not all_for_rendering else list(self.parameters.values())
        )

        # Рендер заголовка / пути
        my_to_render = []
        property_line_render = self.name is not None and (
            self.status == Statuses.MODIFIED or len(to_render_count) > 1
        )
        params_tab_level = tab_level
        if property_line_render:
            rendered_path = RT.make_path(
                self.schema_path + [self.name],
                self.json_path + [self.name],
                ignore=self.config.PATH_MAKER_IGNORE,
            )

            my_to_render.append(
                f"{RT.make_prefix(self.status)} "
                f"{RT.make_tab(self.config, tab_level)}"
                f"{rendered_path}:"
            )
            params_tab_level += 1

        # Рендер параметров
        for param in to_render_count:
            my_to_render.append(param.render(params_tab_level, not property_line_render))

        to_render = "\n".join(my_to_render)

        compare_list = []
        for compare in to_render_count:
            compare_list.append(type(compare))

        return to_render, list(dict.fromkeys([*compare_list]))

    def render(
        self, tab_level: int = 0, all_for_rendering: bool = False
    ) -> tuple[list[str], list[type["Compare"]]]:
        to_return: list[str] = []
        compare_list: list[type["Compare"]] = []

        if all_for_rendering or self.is_for_rendering():
            start_line, start_compare = self.self_render(
                tab_level=tab_level, all_for_rendering=all_for_rendering
            )
            to_return.append(start_line)
            compare_list = list(dict.fromkeys([*compare_list, *start_compare]))

        for prop in self.propertys.values():
            part_lines, part_compare = prop.render(
                tab_level=tab_level, all_for_rendering=all_for_rendering
            )
            to_return += part_lines
            compare_list = list(dict.fromkeys([*compare_list, *part_compare]))

        return to_return, compare_list
