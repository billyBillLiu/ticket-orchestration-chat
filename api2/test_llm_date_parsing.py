#!/usr/bin/env python3
"""
Test script for LLM date parsing functionality
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.async_field_processor import AsyncFieldProcessor

async def test_llm_date_parsing():
    """Test the LLM date parsing with various inputs"""
    
    print("🧪 Testing LLM Date Parsing")
    print("=" * 50)
    
    # Test cases for LLM date parsing
    test_cases = [
        # Standard formats (should work with standard parsing)
        ("2024-01-15", "2024-01-15"),
        ("01/15/2024", "2024-01-15"),
        ("January 15, 2024", "2024-01-15"),
        
        # Natural language (should use LLM)
        ("tomorrow", None),  # Will be dynamic
        ("next Monday", None),  # Will be dynamic
        ("yesterday", None),  # Will be dynamic
        ("in 3 days", None),  # Will be dynamic
        ("next week", None),  # Will be dynamic
        ("end of month", None),  # Will be dynamic
        ("beginning of next month", None),  # Will be dynamic
        ("last Friday", None),  # Will be dynamic
        ("this Friday", None),  # Will be dynamic
        ("next month", None),  # Will be dynamic
    ]
    
    for i, test_case in enumerate(test_cases):
        user_input = test_case[0]
        expected = test_case[1]
        
        print(f"\nTest {i+1}: Date parsing")
        print(f"Input: '{user_input}'")
        print(f"Expected: {expected if expected else 'Dynamic date'}")
        
        try:
            # Process the input using async date parsing
            result = await AsyncFieldProcessor._process_date_async(user_input)
            print(f"Result: {result}")
            
            # Check if result is valid
            if expected:
                if result == expected:
                    print("✅ PASS - Matches expected")
                else:
                    print("❌ FAIL - Doesn't match expected")
            else:
                # For dynamic dates, just check if it's a valid date format
                import re
                if re.match(r'^\d{4}-\d{2}-\d{2}$', result):
                    print("✅ PASS - Valid date format")
                else:
                    print("❌ FAIL - Invalid date format")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 LLM Date Parsing Test Complete")

if __name__ == "__main__":
    asyncio.run(test_llm_date_parsing())
