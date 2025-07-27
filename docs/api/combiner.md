# Parameter Combiner

```{eval-rst}
.. automodule:: jsonschema_diff.combiner
   :members:
   :undoc-members:
   :show-inheritance:
```

## Overview

The `combiner` module is responsible for combining related parameters into composite changes. This is particularly useful for parameters that commonly change together, such as `type` and `format`.

## Key Classes

### ParameterCombiner

The main class that handles parameter combination logic.

## Configuration

The combiner uses the configuration system to determine which parameters can be combined and under what conditions. See the [Configuration Guide](../configuration.md) for details on combination rules.

## Examples

```python
from jsonschema_diff.combiner import ParameterCombiner
from jsonschema_diff.config import Config

combiner = ParameterCombiner(Config.get_combination_rules())
```
