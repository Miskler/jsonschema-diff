#!/usr/bin/env python3
"""Простой тест для вывода различий между схемами."""

from jsonschema_diff import compare_schemas

# Схемы пользователя
old_user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"}
            }
        }
    },
    "required": ["name", "email"]
}

new_user_schema = {
    "type": "object", 
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "country": {"type": "string"}
            },
            "required": ["country"]
        },
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "email", "phone"]
}

print("=== ТЕСТ 1: Схема пользователя ===")
print(compare_schemas(old_user_schema, new_user_schema))

# API схемы
old_api_schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "role": {"type": "string", "enum": ["user", "admin"]}
                },
                "required": ["id", "name"]
            }
        },
        "total": {"type": "integer"}
    }
}

new_api_schema = {
    "type": "object",
    "properties": {
        "users": {
            "type": "array", 
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "role": {"type": "string", "enum": ["user", "admin", "moderator"]},
                    "created_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name", "role"]
            }
        },
        "total": {"type": "integer"},
        "page": {"type": "integer"},
        "per_page": {"type": "integer"}
    },
    "required": ["users", "total"]
}

print("\n=== ТЕСТ 2: API схема ===")
print(compare_schemas(old_api_schema, new_api_schema))

# Сложная вложенная схема
complex_old = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "ssl": {"type": "boolean"}
                    }
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}

complex_new = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object", 
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "ssl": {"type": "boolean"},
                        "pool_size": {"type": "integer"}
                    },
                    "required": ["host", "port"]
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "cache": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "ttl": {"type": "integer"}
                    }
                }
            }
        },
        "version": {"type": "string"}
    }
}

print("\n=== ТЕСТ 3: Сложная вложенная схема ===")
print(compare_schemas(complex_old, complex_new))

# ТЕСТ 4: Проверка различных комбинаций type/format
print("\n=== ТЕСТ 4: Комбинации type/format ===")

test_type_format_old = {
    "type": "object",
    "properties": {
        # Случай 1: И type и format меняются вместе
        "field1": {"type": "string", "format": "date-time"},
        # Случай 2: type и format удаляются вместе (заменяется на integer без format)
        "field2": {"type": "string", "format": "uuid"},
        # Случай 3: Только format удаляется
        "field3": {"type": "string", "format": "email"},
        # Случай 4: Только type меняется
        "field4": {"type": "integer"},
        # Случай 5: Есть format, type не меняется
        "field5": {"type": "string", "format": "date"}
    }
}

test_type_format_new = {
    "type": "object", 
    "properties": {
        # Случай 1: И type и format меняются вместе
        "field1": {"type": "number", "format": "float"},
        # Случай 2: type и format удаляются вместе (заменяется на integer без format)
        "field2": {"type": "integer"},
        # Случай 3: Только format удаляется
        "field3": {"type": "string"},
        # Случай 4: Только type меняется
        "field4": {"type": "number"},
        # Случай 5: Есть format, type не меняется, но format меняется
        "field5": {"type": "string", "format": "time"}
    }
}

print(compare_schemas(test_type_format_old, test_type_format_new))
