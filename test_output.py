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
