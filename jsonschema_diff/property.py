from .abstraction import Statuses
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config
    from .parameter_base import Compare


class Property:
    def __init__(
            self,
            config: "Config",
            schema_path: list[str | int],
            json_path: list[str | int],
            name: str | int,
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

        keys = self._get_keys(self.old_schema, self.new_schema)
        for key in keys:
            old_key = key if key in self.old_schema else None
            old_value = self.old_schema.get(key, None)

            new_key = key if key in self.new_schema else None
            new_value = self.new_schema.get(key, None)

            if key in ["properties", "$defs"]:#, "items"]:
                prop_keys = self._get_keys(old_value, new_value) # list(old_value.keys() | new_value.keys())
                for prop_key in prop_keys:
                    old_to_prop = None if old_value is None else old_value.get(prop_key, None)
                    new_to_prop = None if new_value is None else new_value.get(prop_key, None)

                    prop = Property(
                        config=self.config,
                        schema_path=self.schema_path+[self.name, key],
                        json_path=self.json_path+[self.name],
                        name=prop_key,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop
                    )
                    prop.compare()
                    self.propertys[prop_key] = prop
            elif key in ["prefixItems", "items"]:
                if not isinstance(old_value, list):
                    old_value = [old_value]
                if not isinstance(new_value, list):
                    new_value = [new_value]

                for i in range(max(len(new_value), len(old_value))):
                    old_to_prop = None if old_value is None else old_value[i]
                    new_to_prop = None if new_value is None else new_value[i]

                    prop = Property(
                        config=self.config,
                        schema_path=self.schema_path+[self.name, key],
                        json_path=self.json_path+[self.name],
                        name=i,
                        old_schema=old_to_prop,
                        new_schema=new_to_prop
                    )
                    prop.compare()
                    self.propertys[i] = prop

            else:
                comparator = self.config.COMPARE_RULES.get_comparator_from_values(old_value, new_value)
                comparator = comparator(self.config, self.schema_path, self.json_path, old_key, old_value, new_key, new_value)
                comparator.compare()

                if comparator.is_for_rendering() and self.status == Statuses.UNKNOWN:
                    self.status = Statuses.MODIFIED

                self.parameters[key] = comparator

    def render(self, tab_level: int = 0) -> list[str]:
        my_to_render = []
        for param in self.parameters.values():
            if param.is_for_rendering():
                my_to_render.append(param.render(tab_level))
        to_render = "\n".join(my_to_render)
        
        to_return = [to_render]
        for prop in self.propertys.values():
            to_return += prop.render(tab_level)
        return to_return


