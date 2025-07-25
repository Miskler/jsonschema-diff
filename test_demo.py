#!/usr/bin/env python3
"""
Test script to demonstrate JSON schema differences.
"""

import json
from jsonschema_diff import compare_schemas

def load_schema(filename):
    """Load JSON schema from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=" * 80)
    print("JSON Schema Diff Demo")
    print("=" * 80)
    
    # Test 1: User Profile Schema Evolution
    print("\n🔍 Test 1: User Profile Schema (v1 -> v2)")
    print("-" * 50)
    
    try:
        user_v1 = load_schema('schema_v1.json')
        user_v2 = load_schema('schema_v2.json')
        
        diff = compare_schemas(user_v1, user_v2)
        if diff:
            print(diff)
        else:
            print("No differences found.")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 80)
    
    # Test 2: API Schema Evolution
    print("\n🔍 Test 2: Product API Schema (v1 -> v2)")
    print("-" * 50)
    
    try:
        api_v1 = load_schema('api_schema_v1.json')
        api_v2 = load_schema('api_schema_v2.json')
        
        diff = compare_schemas(api_v1, api_v2)
        if diff:
            print(diff)
        else:
            print("No differences found.")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print("\n" + "=" * 80)
    
    # Test 3: Reverse comparison (v2 -> v1)
    print("\n🔍 Test 3: Reverse Comparison - User Profile (v2 -> v1)")
    print("-" * 60)
    
    try:
        user_v1 = load_schema('schema_v1.json')
        user_v2 = load_schema('schema_v2.json')
        
        diff = compare_schemas(user_v2, user_v1)
        if diff:
            print(diff)
        else:
            print("No differences found.")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    main()
