# Contributing Guide

Thank you for your interest in contributing to JSON Schema Diff! This guide will help you get started with contributing to the project.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of JSON Schema

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/jsonschema-diff.git
   cd jsonschema-diff
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e .[dev]
   # Or install manually:
   pip install pytest coverage black isort mypy sphinx furo
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest
   ```

## 🏗️ Architecture Overview

Understanding the architecture helps you contribute effectively:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ DiffFinder  │───▶│ DiffProcessor │───▶│  Combiner   │
└─────────────┘    └──────────────┘    └─────────────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ PathUtils   │    │RenderProcessor│◀───┤  Config     │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │  Formatter  │
                   └─────────────┘
```

### Module Responsibilities

- **`comparator.py`**: Main orchestration and public API
- **`diff_finder.py`**: Raw difference detection between schemas
- **`diff_processor.py`**: Converts add/remove pairs to changes
- **`combiner.py`**: Combines related parameters using configuration rules
- **`render_processor.py`**: Adds context and structures data for rendering
- **`formatter.py`**: Creates final formatted output with colors
- **`config.py`**: Type-safe configuration classes and rules
- **`path_utils.py`**: Utilities for working with schema paths
- **`context_manager.py`**: Legacy context management (being phased out)
- **`cli.py`**: Command-line interface

## 🧪 Testing

We maintain 99% test coverage. Please ensure your contributions include appropriate tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=jsonschema_diff --cov-report=term-missing

# Run specific test file
pytest tests/test_combiner.py

# Run specific test
pytest tests/test_combiner.py::TestParameterCombiner::test_combine_type_and_format
```

### Writing Tests

1. **Unit tests**: Test individual methods and classes
2. **Integration tests**: Test the full pipeline
3. **Edge cases**: Test boundary conditions and error cases

Example test structure:
```python
class TestNewFeature:
    """Test cases for new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality works as expected."""
        # Setup
        input_data = {...}
        expected = {...}
        
        # Execute
        result = new_feature_function(input_data)
        
        # Assert
        assert result == expected
        
    def test_edge_case(self):
        """Test edge case handling."""
        # Test edge cases, error conditions, etc.
```

### Test Organization

- `tests/test_<module>.py`: Unit tests for each module
- Tests use pytest fixtures for common setup
- Mock external dependencies when appropriate
- Test both success and error paths

## 🎨 Code Style

We use automated tools to maintain code quality:

### Formatting

```bash
# Format code with Black
black jsonschema_diff tests

# Sort imports with isort
isort jsonschema_diff tests

# Check formatting
black --check jsonschema_diff tests
isort --check-only jsonschema_diff tests
```

### Type Checking

```bash
# Run mypy type checking
mypy jsonschema_diff
```

### Code Quality Guidelines

1. **Type hints**: All functions should have type hints
2. **Docstrings**: All public functions and classes need docstrings
3. **Error handling**: Handle edge cases and provide meaningful errors
4. **Testing**: New code must include tests
5. **Documentation**: Update docs for user-facing changes

## 📝 Documentation

### Building Documentation

```bash
cd docs

# Install documentation dependencies
make install-deps

# Generate examples and build HTML
make html

# Live reload during development
make livehtml

# Clean and rebuild
make rebuild
```

### Documentation Structure

- `docs/index.md`: Main documentation page
- `docs/quickstart.md`: Getting started guide
- `docs/configuration.md`: Configuration reference
- `docs/examples/`: Auto-generated examples
- `docs/api/`: API reference (auto-generated)

### Writing Documentation

1. **User-focused**: Write for users, not just developers
2. **Examples**: Include practical, working examples
3. **Clear structure**: Use headers, lists, and formatting
4. **Live examples**: Use the auto-generation system for examples

## 🔄 Contribution Workflow

### 1. Choose What to Work On

- Check [GitHub Issues](https://github.com/your-username/jsonschema-diff/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Propose new features by creating an issue first

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

### 3. Make Your Changes

- Follow the code style guidelines
- Add tests for new functionality
- Update documentation if needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run tests
pytest

# Check coverage
pytest --cov=jsonschema_diff --cov-report=term-missing

# Type checking
mypy jsonschema_diff

# Code formatting
black jsonschema_diff tests
isort jsonschema_diff tests
```

### 5. Update Documentation

```bash
cd docs
make examples  # Regenerate examples if needed
make html      # Build documentation
```

### 6. Commit and Push

```bash
git add .
git commit -m "Add feature: describe your changes"
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill out the PR template
3. Link related issues
4. Wait for review and address feedback

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description**: What happened vs. what you expected
2. **Minimal reproduction**: Smallest possible example that shows the bug
3. **Environment**: Python version, library version, OS
4. **Code sample**: Complete, runnable code that demonstrates the issue

Example bug report:
```
## Bug Description
Schema comparison produces incorrect output when...

## Expected Behavior
Should show: `type: "string" -> "integer"`

## Actual Behavior
Shows: `type: "string"`

## Reproduction
```python
from jsonschema_diff import compare_schemas

old_schema = {"type": "string"}
new_schema = {"type": "integer"}
result = compare_schemas(old_schema, new_schema)
print(result)  # Incorrect output
```

## Environment
- Python 3.9.0
- jsonschema-diff 2.0.0
- Ubuntu 20.04
```

## 💡 Feature Requests

For new features:

1. **Create an issue first**: Discuss the feature before implementing
2. **Explain the use case**: Why is this feature needed?
3. **Propose the API**: How should it work?
4. **Consider compatibility**: Will it break existing code?

## 🎯 Areas for Contribution

### High Priority
- **Performance improvements**: Optimize comparison algorithms
- **New combination rules**: Add support for more parameter combinations
- **CLI enhancements**: Better output formatting, new options
- **Documentation**: More examples, tutorials, use cases

### Medium Priority
- **Custom configuration**: Allow runtime configuration customization
- **Output formats**: JSON, YAML, or other structured outputs
- **Schema validation**: Validate schemas before comparison
- **Internationalization**: Support for different languages

### Advanced
- **Schema evolution tracking**: Track changes across multiple versions
- **Semantic analysis**: Understand schema semantics beyond syntax
- **Performance benchmarking**: Automated performance regression testing
- **Plugin system**: Allow custom comparison logic

## 🏷️ Release Process

For maintainers:

1. **Update version**: Bump version in `pyproject.toml`
2. **Update changelog**: Add new version entry
3. **Tag release**: Create and push git tag
4. **Build package**: `python -m build`
5. **Upload to PyPI**: `twine upload dist/*`
6. **Deploy docs**: Update documentation site

## 📞 Getting Help

- **Documentation**: Check the [docs](https://jsonschema-diff.readthedocs.io)
- **GitHub Issues**: Ask questions or report problems
- **Discussions**: Use GitHub Discussions for general questions
- **Code review**: Tag maintainers in PRs for review

## 🎉 Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Documentation credits
- GitHub contributor graphs

Thank you for contributing to JSON Schema Diff! 🙏

---

*This guide is living documentation. Please suggest improvements via issues or PRs.*
