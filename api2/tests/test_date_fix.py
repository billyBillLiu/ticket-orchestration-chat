#!/usr/bin/env python3
"""
Test script to verify the date parsing fix
"""

import re
from datetime import datetime

def test_date_extraction():
    """Test extracting dates from LLM responses"""
    
    print("🧪 Testing Date Extraction from LLM Responses")
    print("=" * 50)
    
    # Test cases - simulating what LLM might return
    test_cases = [
        # Good cases
        ("2024-01-16", "2024-01-16"),
        ("The date is 2024-01-16", "2024-01-16"),
        ("Here's the date: 2024-01-16", "2024-01-16"),
        ("2024-01-16 is the result", "2024-01-16"),
        
        # Bad cases (what we saw in the error)
        ("Here's a Python solution for your problem:\n\n```Python\nfrom datetime import datetime, timedelta\n\ndef convert_date(date_str):\n    today = datetime.today()\n\n    if date_str == 'tomorrow':\n        return (today + timedelta(days=1", None),
        
        # Edge cases
        ("INVALID_DATE", "INVALID_DATE"),
        ("No date here", None),
        ("2024-13-45", "2024-13-45"),  # Invalid date but valid format
    ]
    
    for i, test_case in enumerate(test_cases):
        llm_response = test_case[0]
        expected = test_case[1]
        
        print(f"\nTest {i+1}: LLM Response Extraction")
        print(f"Input: '{llm_response}'")
        print(f"Expected: {expected}")
        
        try:
            # Clean up the result - remove any extra text and extract just the date
            # Look for YYYY-MM-DD pattern in the response
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', llm_response)
            if date_match:
                result = date_match.group(1)
            else:
                result = llm_response.strip()
            
            print(f"Extracted: {result}")
            
            # Check if result matches expected
            if result == expected:
                print("✅ PASS")
            else:
                print("❌ FAIL - Doesn't match expected")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Date Extraction Test Complete")

if __name__ == "__main__":
    test_date_extraction()
