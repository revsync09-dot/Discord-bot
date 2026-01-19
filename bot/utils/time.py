"""
Time formatting utilities.
Consistent time display across all embeds.
"""

from datetime import datetime, timezone
from typing import Optional


def format_timestamp(
    dt: datetime,
    style: str = "f"
) -> str:
    """
    Format datetime as Discord timestamp.
    
    Args:
        dt: Datetime to format
        style: Discord timestamp style
            - t: Short Time (16:20)
            - T: Long Time (16:20:30)
            - d: Short Date (20/04/2021)
            - D: Long Date (20 April 2021)
            - f: Short Date/Time (20 April 2021 16:20) [default]
            - F: Long Date/Time (Tuesday, 20 April 2021 16:20)
            - R: Relative Time (2 months ago)
    
    Returns:
        Discord timestamp string
    """
    # Ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:{style}>"


def format_relative(dt: datetime) -> str:
    """Format as relative time (e.g., '2 hours ago')."""
    return format_timestamp(dt, style="R")


def format_short_date(dt: datetime) -> str:
    """Format as short date (e.g., '20/04/2021')."""
    return format_timestamp(dt, style="d")


def format_long_date(dt: datetime) -> str:
    """Format as long date (e.g., '20 April 2021')."""
    return format_timestamp(dt, style="D")


def format_short_datetime(dt: datetime) -> str:
    """Format as short date/time (e.g., '20 April 2021 16:20')."""
    return format_timestamp(dt, style="f")


def format_long_datetime(dt: datetime) -> str:
    """Format as long date/time (e.g., 'Tuesday, 20 April 2021 16:20')."""
    return format_timestamp(dt, style="F")


def now_utc() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def from_iso(iso_string: str) -> datetime:
    """Parse ISO 8601 datetime string."""
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))


def to_iso(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()