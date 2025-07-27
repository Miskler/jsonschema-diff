# 📋 Changelog

All notable changes to JSON Schema Diff are documented here.

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [2.0.0] - 2025-01-27

### 🎉 Major Release - Complete Architecture Refactor

This release represents a complete rewrite with modern architecture, comprehensive testing, and powerful new features for production use.

### ✨ Added

#### 🏗️ Modular Pipeline Architecture
- **5-stage processing pipeline** for clean separation of concerns:
  ```
  DiffFinder → DiffProcessor → Combiner → RenderProcessor → Formatter
  ```
- **Type-safe interfaces** between all modules
- **Extensible design** for custom processors and formatters
- **Dependency injection** patterns for testability

#### 🔗 Smart Parameter Combination
- **Configurable combination rules** via `CombinationRule` dataclass
- **Operation-aware combining**: Different behavior for add/remove/change
- **Template-based formatting**: `"{main}/{sub}"` style templates
- **Built-in combinations**:
  - `type` + `format` → `"string/email"` 
  - `minimum` + `maximum` → `"0-100"` (range format)

#### 📍 Context-Aware Display  
- **Intelligent context addition**: Shows related fields when important parameters change
- **Metadata-driven approach**: No more brittle string parsing
- **Configurable context rules**: Define what context to show per parameter
- **Proper grouping**: Context appears with correct spacing and indentation

#### 🎨 Enhanced Output Formatting
- **Beautiful colored output** with optional Click dependency
- **Graceful fallback** when Click not available  
- **Consistent spacing**: No extra blank lines, proper group separation
- **Symbol-based indicators**: `+` (add), `-` (remove), `r` (change), ` ` (context)

#### ⚡ Performance & Reliability
- **99%+ test coverage** across all modules
- **Type-safe codebase** with comprehensive type hints
- **Memory efficient** processing for large schemas
- **Robust error handling** with meaningful messages

#### 🛠️ Developer Experience
- **Comprehensive documentation** with examples and API reference
- **Modern tooling**: Black, isort, mypy, pytest with coverage
- **CI/CD ready**: Makefile with all common development tasks
- **Troubleshooting guide** for common issues
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
