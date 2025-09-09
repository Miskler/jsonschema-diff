from importlib import import_module
from types import ModuleType

from .config_maker import ConfigMaker
from .pypi_interface import JsonSchemaDiff


# Lazy-import подмодуля sphinx (тянет Rich → Sphinx только по требованию)
def __getattr__(name: str) -> ModuleType:  # pragma: no cover
    if name == "sphinx":
        return import_module("jsonschema_diff.sphinx")
    raise AttributeError(name)


__all__ = ["JsonSchemaDiff", "ConfigMaker"]

__version__ = "0.1.6"
