#!/usr/bin/env python3
"""
Simple test to verify the library works correctly.
"""

from jsonschema_diff import SchemaComparator, compare_schemas

def test_simple_schemas():
    """Test with simple schemas to verify basic functionality."""
    print("🧪 Testing Simple Schema Comparison")
    print("-" * 40)
    
    # Simple test case 1: Adding a property
    old_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    new_schema = {
        "type": "object", 
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "email"]
    }
    
    print("Test 1: Adding properties and requirements")
    diff = compare_schemas(old_schema, new_schema)
    print(diff)
    print()

def test_complex_nested():
    """Test with complex nested structures."""
    print("🧪 Testing Complex Nested Schema Comparison")
    print("-" * 45)
    
    old_schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "settings": {
                                "type": "object",
                                "properties": {
                                    "theme": {"type": "string", "enum": ["light", "dark"]},
                                    "lang": {"type": "string", "enum": ["en", "es"]}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    new_schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "avatar": {"type": "string", "format": "uri"},
                            "settings": {
                                "type": "object",
                                "properties": {
                                    "theme": {"type": "string", "enum": ["light", "dark", "auto"]},
                                    "lang": {"type": "string", "enum": ["en", "es", "fr", "de"]},
                                    "notifications": {"type": "boolean", "default": true}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    print("Test 2: Complex nested changes")
    diff = compare_schemas(old_schema, new_schema) 
    print(diff)
    print()

def test_array_changes():
    """Test array modifications."""
    print("🧪 Testing Array Schema Changes")
    print("-" * 35)
    
    old_schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "categories": {
                "type": "array", 
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }
    
    new_schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 10,
                "uniqueItems": True
            },
            "categories": {
                "type": "array",
                "items": {
                    "type": "object", 
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["id", "name", "slug"]
                },
                "minItems": 1
            }
        }
    }
    
    print("Test 3: Array schema modifications")
    diff = compare_schemas(old_schema, new_schema)
    print(diff)
    print()

def test_class_usage():
    """Test using the SchemaComparator class directly."""
    print("🧪 Testing SchemaComparator Class Direct Usage")
    print("-" * 48)
    
    old = {"type": "string", "maxLength": 50}
    new = {"type": "string", "maxLength": 100, "minLength": 1}
    
    comparator = SchemaComparator(old, new)
    result = comparator.compare()
    
    print("Test 4: Direct class usage")
    print(result)
    print()

def main():
    print("=" * 80)
    print("JSON Schema Diff - Simple Functionality Tests")
    print("=" * 80)
    
    try:
        test_simple_schemas()
        test_complex_nested()
        test_array_changes()
        test_class_usage()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
