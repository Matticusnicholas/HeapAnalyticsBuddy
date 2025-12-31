"""
Helper utilities for Heap Analytics Buddy
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as formatted string

    Args:
        format_str: strftime format string

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format a number with thousand separators

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if decimals > 0:
        return f"{value:,.{decimals}f}"
    return f"{int(value):,}"


def format_duration(seconds: float) -> str:
    """
    Format seconds into human-readable duration

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "1h 23m 45s"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if secs > 0:
            return f"{hours}h {mins}m {secs}s"
        return f"{hours}h {mins}m"


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize a string to be safe for use as a filename

    Args:
        filename: Original filename
        replacement: Character to replace invalid chars with

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, replacement, filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')

    # Limit length
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized or "unnamed"


def parse_url_path(url: str) -> str:
    """
    Extract path from URL for display

    Args:
        url: Full URL

    Returns:
        Path portion of URL
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.path or "/"


def abbreviate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Abbreviate text to maximum length

    Args:
        text: Text to abbreviate
        max_length: Maximum length including suffix
        suffix: String to append when truncated

    Returns:
        Abbreviated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_percentage(value: float, total: float, decimals: int = 1) -> float:
    """
    Calculate percentage safely

    Args:
        value: Numerator
        total: Denominator
        decimals: Number of decimal places

    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    return round((value / total) * 100, decimals)


def merge_dicts(*dicts) -> dict:
    """
    Deep merge multiple dictionaries

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if not d:
            continue
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result
