#!/usr/bin/env python3
"""
Simple test for field processing logic
"""

import re
from datetime import datetime
from typing import Any, List

def process_string(user_input: str) -> str:
    """Process string input - just return as is"""
    return user_input

def process_bool(user_input: str) -> bool:
    """Process boolean input"""
    user_input_lower = user_input.lower().strip()
    
    # Common true values
    if user_input_lower in ['true', 'yes', 'y', '1', 'on', 'enabled']:
        return True
    # Common false values
    elif user_input_lower in ['false', 'no', 'n', '0', 'off', 'disabled']:
        return False
    else:
        raise ValueError(f"Invalid boolean value: '{user_input}'. Please use 'true'/'false', 'yes'/'no', or '1'/'0'")

def process_int(user_input: str) -> int:
    """Process integer input - extract numbers from text"""
    # Remove common words and extract numbers
    cleaned = re.sub(r'[^\d\-]', ' ', user_input)
    numbers = re.findall(r'-?\d+', cleaned)
    
    if not numbers:
        raise ValueError(f"No valid number found in: '{user_input}'")
    
    # Take the first number found
    try:
        return int(numbers[0])
    except ValueError:
        raise ValueError(f"Invalid integer: '{numbers[0]}'")

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

def process_time(user_input: str) -> str:
    """Process time input - convert to HH:MM format"""
    user_input = user_input.strip()
    
    # Try common time formats
    time_formats = [
        '%H:%M',         # 14:30
        '%H:%M:%S',      # 14:30:00
        '%I:%M %p',      # 2:30 PM
        '%I:%M:%S %p',   # 2:30:00 PM
        '%I %p',         # 2 PM
        '%H %M',         # 14 30
    ]
    
    for fmt in time_formats:
        try:
            parsed_time = datetime.strptime(user_input, fmt)
            return parsed_time.strftime('%H:%M')
        except ValueError:
            continue
    
    # Try to extract time using regex
    time_patterns = [
        r'(\d{1,2}):(\d{2})(?::(\d{2}))?',  # HH:MM or HH:MM:SS
        r'(\d{1,2})\s*(\d{2})',             # HH MM
        r'(\d{1,2})\s*(am|pm)',             # HH AM/PM
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, user_input.lower())
        if match:
            try:
                if 'am' in user_input.lower() or 'pm' in user_input.lower():
                    # Handle AM/PM format
                    hour = int(match.group(1))
                    period = match.group(2)
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0
                    return f"{hour:02d}:00"
                else:
                    # Handle 24-hour format
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    return f"{hour:02d}:{minute:02d}"
            except (ValueError, IndexError):
                continue
    
    raise ValueError(f"Could not parse time from: '{user_input}'. Please use format HH:MM, 2:30 PM, or similar.")

def process_choice(user_input: str, options: List[str]) -> str:
    """Process choice input - find best match from options"""
    if not options:
        return user_input  # No options available, return as is
    
    user_input_lower = user_input.lower().strip()
    
    # Exact match (case insensitive)
    for option in options:
        if option.lower() == user_input_lower:
            return option
    
    # Partial match
    for option in options:
        if user_input_lower in option.lower() or option.lower() in user_input_lower:
            return option
    
    # If no match found, raise error with available options
    options_str = ", ".join(options)
    raise ValueError(f"Invalid choice: '{user_input}'. Available options: {options_str}")

def process_multi_choice(user_input: str, options: List[str]) -> List[str]:
    """Process multi-choice input - find best matches from options"""
    if not options:
        return [user_input]  # No options available, return as single item
    
    # Split by common delimiters
    choices = re.split(r'[,;|]|\band\b', user_input, flags=re.IGNORECASE)
    choices = [choice.strip() for choice in choices if choice.strip()]
    
    if not choices:
        raise ValueError(f"No valid choices found in: '{user_input}'")
    
    selected_options = []
    for choice in choices:
        try:
            matched_option = process_choice(choice, options)
            if matched_option not in selected_options:
                selected_options.append(matched_option)
        except ValueError as e:
            print(f"⚠️ Could not match choice '{choice}': {e}")
            # Continue with other choices
    
    if not selected_options:
        options_str = ", ".join(options)
        raise ValueError(f"No valid choices found. Available options: {options_str}")
    
    return selected_options

def test_field_processing():
    """Test the field processing functions"""
    
    print("🧪 Testing Field Processing Functions")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # String fields
        ("string", "Hello World", "Hello World", None),
        ("rich_text", "Some rich text with **bold**", "Some rich text with **bold**", None),
        
        # Boolean fields
        ("bool", "true", True, None),
        ("bool", "yes", True, None),
        ("bool", "1", True, None),
        ("bool", "false", False, None),
        ("bool", "no", False, None),
        ("bool", "0", False, None),
        
        # Integer fields
        ("int", "42", 42, None),
        ("int", "The code is 42", 42, None),
        ("int", "Error code -404", -404, None),
        
        # Date fields
        ("date", "2024-01-15", "2024-01-15", None),
        ("date", "01/15/2024", "2024-01-15", None),
        ("date", "January 15, 2024", "2024-01-15", None),
        
        # Time fields
        ("time", "14:30", "14:30", None),
        ("time", "2:30 PM", "14:30", None),
        ("time", "2 PM", "14:00", None),
        
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
        options = test_case[3]
        
        print(f"\nTest {i+1}: {field_type} field")
        print(f"Input: '{user_input}'")
        print(f"Expected: {expected}")
        
        try:
            # Process the input based on field type
            if field_type == "string" or field_type == "rich_text":
                result = process_string(user_input)
            elif field_type == "bool":
                result = process_bool(user_input)
            elif field_type == "int":
                result = process_int(user_input)
            elif field_type == "date":
                result = process_date(user_input)
            elif field_type == "time":
                result = process_time(user_input)
            elif field_type == "choice":
                result = process_choice(user_input, options)
            elif field_type == "multi_choice":
                result = process_multi_choice(user_input, options)
            else:
                result = user_input
            
            print(f"Result: {result}")
            
            # Check if result matches expected
            if result == expected:
                print("✅ PASS")
            else:
                print("❌ FAIL - Result doesn't match expected")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Field Processing Test Complete")

if __name__ == "__main__":
    test_field_processing()
