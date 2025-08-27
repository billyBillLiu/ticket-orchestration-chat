# app/services/async_field_processor.py
from __future__ import annotations
import re
import json
from datetime import datetime, date
from typing import Any, List, Optional, Union
from app.models.ticket_agent import FieldDef
from app.services.llm_service import llm_service, Message as LLMMessage

class AsyncFieldProcessor:
    """Async version of FieldProcessor for better LLM integration"""
    
    @staticmethod
    async def process_field_value(user_input: str, field_def: FieldDef) -> Any:
        """
        Process user input and convert it to the appropriate type based on field definition.
        Returns the processed value or raises ValueError if processing fails.
        """
        print(f"🔧 ASYNC_PROCESSOR: Processing field '{field_def.name}' (type: {field_def.type}) with input: '{user_input}'")
        
        # Clean the input
        user_input = user_input.strip()
        if not user_input:
            raise ValueError(f"Empty input for required field '{field_def.name}'")
        
        try:
            if field_def.type == "string":
                return AsyncFieldProcessor._process_string(user_input)
            elif field_def.type == "rich_text":
                return AsyncFieldProcessor._process_rich_text(user_input)
            elif field_def.type == "bool":
                return AsyncFieldProcessor._process_bool(user_input)
            elif field_def.type == "int":
                return AsyncFieldProcessor._process_int(user_input)
            elif field_def.type == "date":
                return await AsyncFieldProcessor._process_date_async(user_input)
            elif field_def.type == "time":
                return AsyncFieldProcessor._process_time(user_input)
            elif field_def.type == "choice":
                return await AsyncFieldProcessor._process_choice_async(user_input, field_def)
            elif field_def.type == "multi_choice":
                return await AsyncFieldProcessor._process_multi_choice_async(user_input, field_def)
            elif field_def.type in ["file", "files"]:
                return AsyncFieldProcessor._process_file(user_input)
            else:
                # Default to string for unknown types
                return user_input
                
        except Exception as e:
            print(f"❌ ASYNC_PROCESSOR: Error processing field '{field_def.name}': {e}")
            raise ValueError(f"Failed to process field '{field_def.name}': {str(e)}")
    
    @staticmethod
    def _process_string(user_input: str) -> str:
        """Process string input - just return as is"""
        return user_input
    
    @staticmethod
    def _process_rich_text(user_input: str) -> str:
        """Process rich text input - just return as is"""
        return user_input
    
    @staticmethod
    def _process_bool(user_input: str) -> bool:
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
    
    @staticmethod
    def _process_int(user_input: str) -> int:
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
    
    @staticmethod
    async def _process_date_async(user_input: str) -> str:
        """Process date input - convert to ISO format with LLM assistance"""
        user_input = user_input.strip()
        
        # Try common date formats first
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
        
        # If standard parsing fails, try LLM assistance
        try:
            return await AsyncFieldProcessor._llm_parse_date(user_input)
        except Exception as e:
            print(f"⚠️ ASYNC_PROCESSOR: LLM date parsing failed: {e}")
            raise ValueError(f"Could not parse date from: '{user_input}'. Please use format YYYY-MM-DD, MM/DD/YYYY, or similar.")
    
    @staticmethod
    def _process_date(user_input: str) -> str:
        """Process date input - convert to ISO format (synchronous version)"""
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
    
    @staticmethod
    def _process_time(user_input: str) -> str:
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
    
    @staticmethod
    async def _process_choice_async(user_input: str, field_def: FieldDef) -> str:
        """Process choice input - find best match from options using LLM"""
        if not field_def.options:
            return user_input  # No options available, return as is
        
        user_input_lower = user_input.lower().strip()
        
        # Exact match (case insensitive)
        for option in field_def.options:
            if option.lower() == user_input_lower:
                return option
        
        # Partial match
        for option in field_def.options:
            if user_input_lower in option.lower() or option.lower() in user_input_lower:
                return option
        
        # Fuzzy match using LLM
        try:
            return await AsyncFieldProcessor._llm_match_choice(user_input, field_def.options)
        except Exception as e:
            print(f"⚠️ ASYNC_PROCESSOR: LLM matching failed: {e}")
            # If LLM fails, raise error with available options
            options_str = ", ".join(field_def.options)
            raise ValueError(f"Invalid choice: '{user_input}'. Available options: {options_str}")
    
    @staticmethod
    async def _process_multi_choice_async(user_input: str, field_def: FieldDef) -> List[str]:
        """Process multi-choice input - find best matches from options"""
        if not field_def.options:
            return [user_input]  # No options available, return as single item
        
        # Split by common delimiters
        choices = re.split(r'[,;|]|\band\b', user_input, flags=re.IGNORECASE)
        choices = [choice.strip() for choice in choices if choice.strip()]
        
        if not choices:
            raise ValueError(f"No valid choices found in: '{user_input}'")
        
        selected_options = []
        for choice in choices:
            try:
                matched_option = await AsyncFieldProcessor._process_choice_async(choice, field_def)
                if matched_option not in selected_options:
                    selected_options.append(matched_option)
            except ValueError as e:
                print(f"⚠️ ASYNC_PROCESSOR: Could not match choice '{choice}': {e}")
                # Continue with other choices
        
        if not selected_options:
            options_str = ", ".join(field_def.options)
            raise ValueError(f"No valid choices found. Available options: {options_str}")
        
        return selected_options
    
    @staticmethod
    def _process_file(user_input: str) -> str:
        """Process file input - for now just return the input"""
        return user_input
    
    @staticmethod
    async def _llm_match_choice(user_input: str, options: List[str]) -> str:
        """Use LLM to find the best match from available options"""
        prompt = f"""Given the user input "{user_input}" and the available options:
{json.dumps(options, indent=2)}

Please select the best matching option. Return ONLY the exact option text, nothing else.

If no option matches well, return "NO_MATCH"."""

        try:
            messages = [LLMMessage(role="user", content=prompt)]
            response = await llm_service.generate_non_streaming_response(
                messages=messages,
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.content.strip()
            
            # Check if result is in options
            if result in options:
                return result
            elif result == "NO_MATCH":
                options_str = ", ".join(options)
                raise ValueError(f"No good match found for '{user_input}'. Available options: {options_str}")
            else:
                # Try to find partial match
                for option in options:
                    if result.lower() in option.lower() or option.lower() in result.lower():
                        return option
                
                options_str = ", ".join(options)
                raise ValueError(f"Invalid choice: '{user_input}'. Available options: {options_str}")
                
        except Exception as e:
            print(f"❌ ASYNC_PROCESSOR: LLM matching failed: {e}")
            options_str = ", ".join(options)
            raise ValueError(f"Invalid choice: '{user_input}'. Available options: {options_str}")
    
    @staticmethod
    async def _llm_parse_date(user_input: str) -> str:
        """Use LLM to parse and standardize date input"""
        prompt = f"""You are a date parser. Convert the input "{user_input}" to YYYY-MM-DD format.

Rules:
- "tomorrow" = today + 1 day
- "yesterday" = today - 1 day  
- "next Monday" = next Monday's date
- "in 3 days" = today + 3 days
- "next week" = today + 7 days
- "end of month" = last day of current month
- "beginning of next month" = first day of next month

IMPORTANT: Return ONLY the date in YYYY-MM-DD format. No explanations, no code, no other text.

Example responses:
- Input: "tomorrow" → Output: "2024-01-16"
- Input: "next Monday" → Output: "2024-01-22"
- Input: "invalid" → Output: "INVALID_DATE"

Your response:"""

        try:
            messages = [LLMMessage(role="user", content=prompt)]
            response = await llm_service.generate_non_streaming_response(
                messages=messages,
                temperature=0.1,
                max_tokens=20
            )
            
            result = response.content.strip()
            
            # Clean up the result - remove any extra text and extract just the date
            # Look for YYYY-MM-DD pattern in the response
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', result)
            if date_match:
                result = date_match.group(1)
            
            # Validate the result is a proper date format
            if result == "INVALID_DATE":
                raise ValueError(f"LLM could not parse date from: '{user_input}'")
            
            # Check if result matches YYYY-MM-DD format
            if re.match(r'^\d{4}-\d{2}-\d{2}$', result):
                # Validate it's a real date
                try:
                    datetime.strptime(result, '%Y-%m-%d')
                    return result
                except ValueError:
                    raise ValueError(f"LLM returned invalid date format: '{result}'")
            else:
                raise ValueError(f"LLM returned invalid date format: '{result}'. Expected YYYY-MM-DD")
                
        except Exception as e:
            print(f"❌ ASYNC_PROCESSOR: LLM date parsing failed: {e}")
            raise ValueError(f"Could not parse date from: '{user_input}'. Please use format YYYY-MM-DD, MM/DD/YYYY, or similar.")

# Create a singleton instance
async_field_processor = AsyncFieldProcessor()
