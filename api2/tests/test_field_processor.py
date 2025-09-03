#!/usr/bin/env python3
"""
Test script for the field processor
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.field_processor import field_processor
from app.models.ticket_agent import FieldDef

def test_field_processor():
    """Test the field processor with various field types"""
    
    print("🧪 Testing Field Processor")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # String fields
        ("string", "Hello World", "Hello World"),
        ("rich_text", "Some rich text with **bold**", "Some rich text with **bold**"),
        
        # Boolean fields
        ("bool", "true", True),
        ("bool", "yes", True),
        ("bool", "1", True),
        ("bool", "false", False),
        ("bool", "no", False),
        ("bool", "0", False),
        
        # Integer fields
        ("int", "42", 42),
        ("int", "The code is 42", 42),
        ("int", "Error code -404", -404),
        
        # Date fields
        ("date", "2024-01-15", "2024-01-15"),
        ("date", "01/15/2024", "2024-01-15"),
        ("date", "January 15, 2024", "2024-01-15"),
        
        # Time fields
        ("time", "14:30", "14:30"),
        ("time", "2:30 PM", "14:30"),
        ("time", "2 PM", "14:00"),
        
        # Choice fields
        ("choice", "critical", "critical", ["critical", "high", "medium", "low"]),
        ("choice", "high priority", "high", ["critical", "high", "medium", "low"]),
        
        # Multi-choice fields
        ("multi_choice", "critical, high", ["critical", "high"], ["critical", "high", "medium", "low"]),
        ("multi_choice", "critical and high", ["critical", "high"], ["critical", "high", "medium", "low"]),
    ]
    
    for i, test_case in enumerate(test_cases):
        field_type = test_case[0]
        user_input = test_case[1]
        expected = test_case[2]
        options = test_case[3] if len(test_case) > 3 else None
        
        print(f"\nTest {i+1}: {field_type} field")
        print(f"Input: '{user_input}'")
        print(f"Expected: {expected}")
        
        try:
            # Create field definition
            field_def = FieldDef(
                name="test_field",
                type=field_type,
                description="Test field",
                options=options
            )
            
            # Process the input
            result = field_processor.process_field_value(user_input, field_def)
            print(f"Result: {result}")
            
            # Check if result matches expected
            if result == expected:
                print("✅ PASS")
            else:
                print("❌ FAIL - Result doesn't match expected")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Field Processor Test Complete")

if __name__ == "__main__":
    test_field_processor()
