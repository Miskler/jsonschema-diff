# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-27

### 🎉 Major Release - Complete Architecture Refactor

This is a complete rewrite of JSON Schema Diff with a modular architecture, comprehensive testing, and powerful new features.

### ✨ Added

#### New Modular Architecture
- **5-stage pipeline**: `DiffFinder` → `DiffProcessor` → `Combiner` → `RenderProcessor` → `Formatter`
- **Separation of concerns**: Each module has a single, well-defined responsibility
- **Clean interfaces**: Clear APIs between modules for maintainability

#### Parameter Combination System
- **Configurable combination rules**: Combine related parameters like `type` + `format`
- **Operation-specific control**: Different combination behavior for add/remove/change operations
- **Virtual parameter creation**: Create combined parameters from schema context
- **Template-based formatting**: Flexible display templates like `"{main}/{sub}"`

#### Context Visualization
- **Intelligent context display**: Show related fields when important parameters change
- **Metadata-driven approach**: Uses structured metadata instead of string parsing
- **Configurable context rules**: Define what context to show for each parameter type
- **Proper grouping**: Context appears immediately after main changes with correct spacing

#### Type-Safe Configuration
- **Dataclass-based config**: Replaced `Dict[str, Any]` with strongly-typed classes
- **Immutable configuration**: Frozen dataclasses prevent accidental modification
- **Comprehensive type hints**: Full type safety throughout the codebase
- **Enum-based modes**: Type-safe operation modes and combination strategies

#### Advanced Output Formatting  
- **Proper line spacing**: Correct empty lines between groups, no gaps within groups
- **Order preservation**: Maintains field order from original schemas
- **DiffGroup metadata**: Structured approach to grouping related changes
- **Enhanced path formatting**: Improved readability of schema paths

#### Comprehensive Testing
- **99% test coverage**: Extensive unit tests covering all modules and edge cases
- **Integration tests**: Full pipeline testing with real-world scenarios
- **Property-based testing**: Robust validation of core functionality
- **Mock-based testing**: Isolated testing of individual components

#### Enhanced CLI
- **Improved error handling**: Better error messages and exit codes
- **Click integration**: Modern CLI framework with proper help and validation
- **File validation**: Robust input validation and error reporting

### 🔄 Changed

#### Breaking Changes
- **New API structure**: Modular design replaces monolithic comparator
- **Configuration format**: Type-safe dataclasses replace dictionaries
- **Import paths**: New module organization affects import statements
- **Output format**: Improved formatting may differ from v1.x

#### Improved Functionality
- **Better diff detection**: More accurate identification of schema changes
- **Enhanced combination logic**: Smarter parameter combination with granular control
- **Improved context handling**: More relevant and useful context information
- **Cleaner output**: Better spacing, grouping, and visual hierarchy

### 🐛 Fixed

#### Core Issues
- **Order preservation**: Fixed loss of field order during comparison
- **Duplicate context**: Eliminated duplicate context entries
- **Spacing problems**: Corrected empty line placement in output
- **Memory leaks**: Resolved circular references and resource management

#### Edge Cases
- **Empty schemas**: Proper handling of empty or missing schema properties
- **Nested structures**: Correct processing of deeply nested objects and arrays
- **Type coercion**: Consistent handling of type conversions and comparisons
- **Path formatting**: Fixed edge cases in schema path representation

### 🏗️ Technical Improvements

#### Code Quality
- **Modular design**: Clean separation of concerns across modules
- **Type safety**: Comprehensive type hints and mypy compliance
- **Documentation**: Extensive docstrings and API documentation
- **Error handling**: Robust error handling throughout the pipeline

#### Performance
- **Optimized algorithms**: More efficient difference detection and processing
- **Reduced memory usage**: Better memory management and object lifecycle
- **Faster execution**: Streamlined pipeline reduces processing overhead

#### Maintainability
- **Clear interfaces**: Well-defined APIs between modules
- **Testable code**: High test coverage enables confident refactoring
- **Extensible design**: Easy to add new features and combination rules
- **Documentation**: Comprehensive guides and examples

### 📚 Documentation

#### New Documentation Site
- **Sphinx + Furo theme**: Professional documentation with modern design
- **Auto-generated examples**: Live examples generated from actual code execution
- **Comprehensive API docs**: Complete reference for all classes and methods
- **User guides**: Step-by-step tutorials and configuration guides

#### Content
- **Architecture overview**: Detailed explanation of the 5-stage pipeline
- **Configuration guide**: How to customize behavior and rules
- **Examples collection**: Real-world scenarios and use cases
- **Contributing guide**: How to contribute to the project

### 🔧 Development

#### Testing Infrastructure
- **Pytest framework**: Modern testing with fixtures and parametrization
- **Coverage reporting**: Detailed coverage analysis and reporting
- **CI/CD integration**: Automated testing and quality checks
- **Mock frameworks**: Comprehensive mocking for isolated testing

#### Development Tools
- **Type checking**: mypy integration for static type analysis
- **Code formatting**: Black and isort for consistent code style
- **Linting**: flake8 and pylint for code quality enforcement
- **Documentation**: Sphinx with automatic API documentation generation

## [1.x.x] - Legacy Versions

Previous versions used a monolithic architecture. See git history for details on 1.x releases.

---

## Migration Guide

### From 1.x to 2.0

#### Import Changes
```python
# Old (1.x)
from jsonschema_diff import compare_schemas

# New (2.0) - Same import works!
from jsonschema_diff import compare_schemas

# New modular imports available
from jsonschema_diff import SchemaComparator
from jsonschema_diff.config import Config
```

#### API Changes
```python
# Old and new - both work the same
result = compare_schemas(old_schema, new_schema)

# New - direct class usage
comparator = SchemaComparator(old_schema, new_schema)
result = comparator.compare()
```

#### Configuration Access
```python
# New - type-safe configuration access
from jsonschema_diff.config import Config

context_params = Config.get_context_params("type")
combination_rules = Config.get_combination_rules()
display_mode = Config.get_display_mode("append")
```

#### Output Format
- Output format has improved but may differ slightly
- Better spacing and grouping
- Enhanced context display
- Preserved field order

The basic API remains the same, so most code will work without changes. The new modular architecture provides much more power and flexibility for advanced use cases.
