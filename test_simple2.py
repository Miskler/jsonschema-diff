#!/usr/bin/env python3
"""Ещё один простой тест с другими примерами схем."""

from jsonschema_diff import compare_schemas

# Тест 1: Простое добавление полей
simple_old = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"}
    },
    "required": ["id"]
}

simple_new = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "name"]
}

print("=== Простое добавление полей ===")
print(compare_schemas(simple_old, simple_new))

# Тест 2: Изменение типов
type_old = {
    "type": "object", 
    "properties": {
        "count": {"type": "integer"},
        "active": {"type": "boolean"},
        "tags": {"type": "array", "items": {"type": "string"}}
    }
}

type_new = {
    "type": "object",
    "properties": {
        "count": {"type": "number"},
        "active": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "integer"}}
    }
}

print("\n=== Изменение типов ===")
print(compare_schemas(type_old, type_new))

# Тест 3: Удаление полей
removal_old = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "body": {"type": "string"},
        "author": {"type": "string"},
        "deprecated_field": {"type": "string"},
        "legacy_data": {
            "type": "object",
            "properties": {
                "old_format": {"type": "string"}
            }
        }
    },
    "required": ["title", "author"]
}

removal_new = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "body": {"type": "string"},
        "author": {"type": "string"}
    },
    "required": ["title"]
}

print("\n=== Удаление полей ===")
print(compare_schemas(removal_old, removal_new))

# Тест 4: Сложные изменения в массивах
array_old = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "integer"}
                }
            }
        },
        "categories": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

array_new = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object", 
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "number"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"}
                        }
                    }
                },
                "required": ["name"]
            }
        },
        "categories": {
            "type": "array",
            "items": {"type": "object", "properties": {"id": {"type": "string"}, "label": {"type": "string"}}}
        }
    }
}

print("\n=== Сложные изменения в массивах ===") 
print(compare_schemas(array_old, array_new))
