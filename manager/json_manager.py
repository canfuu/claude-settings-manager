"""
JSON Manager for Claude Settings Manager
Handles JSON validation, formatting, and error handling
"""
import json
from typing import Tuple, Optional, Any


class JsonManager:
    """Manages JSON validation and formatting"""

    @staticmethod
    def validate_json(json_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a string is valid JSON

        Args:
            json_str: String to validate

        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        if not json_str or not json_str.strip():
            return False, "JSON content cannot be empty"

        try:
            json.loads(json_str)
            return True, None
        except json.JSONDecodeError as e:
            # Create a more user-friendly error message
            error_msg = f"JSON Error at line {e.lineno}, column {e.colno}: {e.msg}"
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def format_json(json_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Format JSON string with proper indentation

        Args:
            json_str: String to format

        Returns:
            Tuple of (success: bool, formatted_json: Optional[str], error_message: Optional[str])
        """
        is_valid, error_msg = JsonManager.validate_json(json_str)
        if not is_valid:
            return False, None, error_msg

        try:
            parsed = json.loads(json_str)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=False)
            return True, formatted, None
        except Exception as e:
            return False, None, f"Formatting error: {str(e)}"

    @staticmethod
    def format_dict(data: dict) -> str:
        """
        Format a dictionary as a JSON string

        Args:
            data: Dictionary to format

        Returns:
            Formatted JSON string
        """
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)

    @staticmethod
    def parse_json(json_str: str) -> Tuple[bool, Optional[Any], Optional[str]]:
        """
        Parse JSON string into a Python object

        Args:
            json_str: String to parse

        Returns:
            Tuple of (success: bool, parsed_data: Optional[Any], error_message: Optional[str])
        """
        is_valid, error_msg = JsonManager.validate_json(json_str)
        if not is_valid:
            return False, None, error_msg

        try:
            parsed = json.loads(json_str)
            return True, parsed, None
        except Exception as e:
            return False, None, f"Parsing error: {str(e)}"

    @staticmethod
    def get_json_error_context(json_str: str, line_num: int, context_lines: int = 2) -> str:
        """
        Get context around a JSON error line

        Args:
            json_str: Original JSON string
            line_num: Line number of the error (1-based)
            context_lines: Number of lines to show before and after

        Returns:
            String with context around the error
        """
        lines = json_str.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)

        context = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            line_num_str = str(i + 1).rjust(4)
            context.append(f"{line_num_str}{prefix}{lines[i]}")

        return '\n'.join(context)
