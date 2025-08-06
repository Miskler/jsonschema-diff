from .abstraction import Statuses, ToCompare
from typing import Any, TYPE_CHECKING
from .tool_render import RenderTool as RT

if TYPE_CHECKING:
    from .config import Config
    from .parameter_base import Compare


class Property:
    def __init__(
            self,
            config: "Config",
            schema_path: list[str | int],
            json_path: list[str | int],
            name: str | int | None,
            old_schema: dict | None,
            new_schema: dict | None
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
    def json_path_with_name(self):
        json_path_with_name = self.json_path
        if self.name is not None:
            json_path_with_name = self.json_path+[self.name]

        return json_path_with_name

    @property
    def schema_path_with_name(self):
        schema_path_with_name = self.schema_path
        if self.name is not None:
            schema_path_with_name = self.schema_path+[self.name]

        return schema_path_with_name

    def _get_keys(self, old, new):
        if not isinstance(old, dict):
            old = {}
        if not isinstance(new, dict):
            new = {}
        return list(old.keys() | new.keys())

    def compare(self): 
        if len(self.old_schema) <= 0:
            self.status = Statuses.ADDED
        elif len(self.new_schema) <= 0:
            self.status = Statuses.DELETED

        parameters_subset = {}
        keys = self._get_keys(self.old_schema, self.new_schema)
        for key in keys:
            old_key = key if key in self.old_schema else None
            old_value = self.old_schema.get(key, None)

            new_key = key if key in self.new_schema else None
            new_value = self.new_schema.get(key, None)

            if key in ["properties", "$defs"]:
                prop_keys = self._get_keys(old_value, new_value)
                for prop_key in prop_keys:
                    old_to_prop = None if old_value is None else old_value.get(prop_key, None)
                    new_to_prop = None if new_value is None else new_value.get(prop_key, None)

                    prop = Property(
                        config=self.config,
                        schema_path=self.schema_path_with_name+[key],
                        json_path=self.json_path_with_name,
                        name=prop_key,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop
                    )
                    prop.compare()
                    self.propertys[prop_key] = prop
            elif key in ["prefixItems", "items"]:
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
                        schema_path=self.schema_path_with_name+[key],
                        json_path=self.json_path_with_name,
                        name=i,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop
                    )
                    prop.compare()
                    self.propertys[i] = prop
            else:
                parameters_subset[key] = {
                    "comparator": self.config.COMPARE_RULES.get_comparator_from_values(key,
                                                                                       old_value,
                                                                                       new_value),
                    "to_compare": ToCompare(old_key=old_key,
                                            old_value=old_value,
                                            new_key=new_key,
                                            new_value=new_value)
                }
        
        result_combine = self.config.COMBINER.combine(parameters_subset)

        for keys, values in result_combine.items():
            comparator = values["comparator"]
            comparator = comparator(self.config,
                                    self.schema_path_with_name,
                                    self.json_path_with_name,
                                    values["to_compare"])

            comparator.compare()

            if comparator.is_for_rendering() and self.status == Statuses.UNKNOWN:
                self.status = Statuses.MODIFIED

            self.parameters[keys] = comparator

    def render(self, tab_level: int = 0) -> list[str]:
        to_render_count = []
        for param in self.parameters.values():
            if param.is_for_rendering():
                to_render_count.append(param)

        my_to_render = []
        property_line_render = self.name is not None and (self.status != Statuses.MODIFIED or len(to_render_count) > 1)
        params_tab_level = tab_level
        if property_line_render:
            my_to_render.append(f"{RT.make_prefix(self.status)} {RT.make_tab(self.config, tab_level)}{RT.make_path(self.schema_path+[self.name], self.json_path+[self.name], ignore=self.config.PATH_MAKER_IGNORE)}:")
            params_tab_level += 1

        for param in to_render_count:
            my_to_render.append(param.render(params_tab_level, not property_line_render))

        to_render = "\n".join(my_to_render)

        #else:
        #    to_render = f"{RT.make_prefix(self.status)} {RT.make_tab(self.config, tab_level)}{RT.make_path(self.schema_path+[self.name], self.json_path+[self.name])}"
        
        to_return = [to_render]
        #if self.status not in [Statuses.DELETED, Statuses.NO_DIFF]:
        for prop in self.propertys.values():
            to_return += prop.render(tab_level)
        return to_return


