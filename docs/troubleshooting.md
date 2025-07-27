# Troubleshooting Guide

This guide helps you resolve common issues when using JSON Schema Diff.

## 🚨 Common Issues

### Installation Problems

#### Issue: `pip install` fails with dependency conflicts

**Solution:**
```bash
# Create a fresh virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install jsonschema-diff
```

#### Issue: Click import errors or no colored output

**Symptoms:**
- Warning: "Colored output enabled but Click not installed"
- No colored output in CLI

**Solution:**
```bash
# Install with optional click dependency
pip install "jsonschema-diff[cli]"

# Or install click separately
pip install click
```

### Schema Comparison Issues

#### Issue: Unexpected diff results

**Common Causes:**
1. **Different schema formats**: Ensure both schemas use the same JSON Schema version
2. **Property order**: JSON Schema properties are order-independent
3. **Default values**: Missing vs. explicit default values are treated differently

**Debug Steps:**
```python
from jsonschema_diff import compare_schemas
from jsonschema_diff.config import Config

# Enable debug mode for detailed output
Config.set_debug_mode(True)  # If this method exists

# Compare schemas step by step
print("Old schema:", old_schema)
print("New schema:", new_schema)
result = compare_schemas(old_schema, new_schema)
print("Differences:", result)
```

#### Issue: Missing context information

**Problem**: Related fields not shown when expected

**Solution:**
```python
from jsonschema_diff.config import Config

# Check current context configuration
context_params = Config.get_context_params("type")
print("Context parameters for 'type':", context_params)

# Context is only shown for meaningful changes
# Not shown if values are identical
```

### Configuration Issues

#### Issue: Custom combination rules not working

**Check:**
1. Rule syntax is correct
2. Parameter names match exactly
3. Combine modes are appropriate

```python
from jsonschema_diff.config import Config, CombinationRule, CombineMode

# Verify rule is registered
rules = Config.get_combination_rules()
for rule in rules:
    if rule.main_param == "your_param":
        print(f"Found rule: {rule}")
        break
else:
    print("Rule not found - check registration")
```

### Performance Issues

#### Issue: Slow comparison for large schemas

**Solutions:**
1. **Pre-process schemas**: Remove unnecessary metadata
2. **Use streaming**: For very large schemas, consider breaking them into smaller parts
3. **Profile bottlenecks**:

```python
import time
start = time.time()
result = compare_schemas(old_schema, new_schema)
print(f"Comparison took: {time.time() - start:.2f}s")
```

## 🐛 Reporting Bugs

### Before Reporting

1. **Update to latest version**:
   ```bash
   pip install --upgrade jsonschema-diff
   ```

2. **Check existing issues**: Search [GitHub Issues](https://github.com/your-org/jsonschema-diff/issues)

3. **Create minimal reproduction**:
   ```python
   # Minimal example that reproduces the issue
   from jsonschema_diff import compare_schemas
   
   old_schema = {"type": "string"}  # Simplest possible
   new_schema = {"type": "integer"}
   
   result = compare_schemas(old_schema, new_schema)
   print(result)  # Show unexpected output
   ```

### Bug Report Template

Include the following information:

**Environment:**
- Python version: `python --version`
- Library version: `pip show jsonschema-diff`
- Operating system
- Click version (if using CLI): `pip show click`

**Schemas:**
```json
{
  "old_schema": { ... },
  "new_schema": { ... }
}
```

**Expected vs Actual:**
- What you expected to see
- What actually happened
- Any error messages or warnings

**Code to Reproduce:**
```python
# Minimal code that reproduces the issue
```

## 💡 Tips & Best Practices

### Schema Design for Better Diffs

1. **Use consistent property order**: While not required, it makes diffs cleaner
2. **Explicit defaults**: Specify default values explicitly rather than relying on implicit ones
3. **Meaningful descriptions**: Use `description` fields for important properties

### Performance Optimization

1. **Remove metadata**: Strip documentation and examples before comparison if not needed
2. **Use specific paths**: When comparing large schemas, focus on specific paths if possible
3. **Cache results**: For repeated comparisons, cache processed schemas

### Custom Configuration

```python
from jsonschema_diff.config import Config

# Customize for your use case
Config.set_use_colors(False)  # Disable colors for logs
# Add custom combination rules for domain-specific parameters
```

## 📖 Additional Resources

- [Configuration Guide](configuration.md) - Detailed configuration options
- [API Reference](api/index.md) - Complete API documentation  
- [Examples](examples/index.md) - Real-world usage examples
- [Contributing](contributing.md) - How to contribute to the project
