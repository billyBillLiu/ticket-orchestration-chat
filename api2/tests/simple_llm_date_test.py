#!/usr/bin/env python3
"""
Simple test for LLM date parsing functionality
"""

import re
from datetime import datetime

def test_date_parsing():
    """Test date parsing with various inputs"""
    
    print("🧪 Testing Date Parsing")
    print("=" * 50)
    
    # Test cases for date parsing
    test_cases = [
        # Standard formats (should work with standard parsing)
        ("2024-01-15", "2024-01-15"),
        ("01/15/2024", "2024-01-15"),
        ("January 15, 2024", "2024-01-15"),
        ("Jan 15, 2024", "2024-01-15"),
        ("15 January 2024", "2024-01-15"),
        ("15 Jan 2024", "2024-01-15"),
        
        # Edge cases
        ("2024/01/15", "2024-01-15"),
        ("1/15/2024", "2024-01-15"),
        ("1/5/2024", "2024-01-05"),
    ]
    
    for i, test_case in enumerate(test_cases):
        user_input = test_case[0]
        expected = test_case[1]
        
        print(f"\nTest {i+1}: Date parsing")
        print(f"Input: '{user_input}'")
        print(f"Expected: {expected}")
        
        try:
            # Process the input using standard date parsing
            result = process_date(user_input)
            print(f"Result: {result}")
            
            # Check if result matches expected
            if result == expected:
                print("✅ PASS")
            else:
                print("❌ FAIL - Doesn't match expected")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Date Parsing Test Complete")

def process_date(user_input: str) -> str:
    """Process date input - convert to ISO format"""
    user_input = user_input.strip()
    
    # Try common date formats
    date_formats = [
        '%Y-%m-%d',      # 2024-01-15
        '%m/%d/%Y',      # 01/15/2024
        '%d/%m/%Y',      # 15/01/2024
        '%Y/%m/%d',      # 2024/01/15
        '%B %d, %Y',     # January 15, 2024
        '%b %d, %Y',     # Jan 15, 2024
        '%d %B %Y',      # 15 January 2024
        '%d %b %Y',      # 15 Jan 2024
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(user_input, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matches, try to extract date using regex
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
        r'(\d{4})/(\d{1,2})/(\d{1,2})',  # YYYY/MM/DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, user_input)
        if match:
            try:
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    # Try both MM/DD and DD/MM for ambiguous formats
                    try:
                        parsed_date = datetime(int(year), int(month), int(day))
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        # Try DD/MM format
                        parsed_date = datetime(int(year), int(day), int(month))
                        return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    raise ValueError(f"Could not parse date from: '{user_input}'. Please use format YYYY-MM-DD, MM/DD/YYYY, or similar.")

if __name__ == "__main__":
    test_date_parsing()
