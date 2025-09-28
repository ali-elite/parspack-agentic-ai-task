from datetime import datetime, timedelta
from typing import Dict, Any
from pydantic import BaseModel
from agents import function_tool

class CurrentDateInfo(BaseModel):
    current_date: str
    current_time: str
    current_datetime: str
    day_of_week: str
    tomorrow_date: str
    yesterday_date: str
    week_start: str
    week_end: str
    formatted_persian_date: str
    unix_timestamp: int

@function_tool
def get_current_date_info() -> CurrentDateInfo:
    """
    Get comprehensive current date and time information.
    
    Returns current date, time, day of week, tomorrow's date, and other useful date calculations.
    Very useful for processing relative date requests like "tomorrow", "next week", etc.
    """
    now = datetime.now()
    
    # Calculate related dates
    tomorrow = now + timedelta(days=1)
    yesterday = now - timedelta(days=1)
    
    # Week calculations (Monday as start of week)
    days_since_monday = now.weekday()
    week_start = now - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    # Persian day names
    persian_days = {
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه', 
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه',
        'Saturday': 'شنبه',
        'Sunday': 'یکشنبه'
    }
    
    day_name_english = now.strftime('%A')
    day_name_persian = persian_days.get(day_name_english, day_name_english)
    
    return CurrentDateInfo(
        current_date=now.strftime('%Y-%m-%d'),
        current_time=now.strftime('%H:%M:%S'),
        current_datetime=now.strftime('%Y-%m-%d %H:%M:%S'),
        day_of_week=day_name_english,
        tomorrow_date=tomorrow.strftime('%Y-%m-%d'),
        yesterday_date=yesterday.strftime('%Y-%m-%d'),
        week_start=week_start.strftime('%Y-%m-%d'),
        week_end=week_end.strftime('%Y-%m-%d'),
        formatted_persian_date=f"{day_name_persian} {now.strftime('%Y/%m/%d')}",
        unix_timestamp=int(now.timestamp())
    )

@function_tool
def calculate_future_date(days_ahead: int) -> Dict[str, Any]:
    """
    Calculate a future date based on days from today.
    
    Args:
        days_ahead: Number of days from today (positive for future, negative for past)
    
    Returns:
        Dictionary with the calculated date information
    """
    target_date = datetime.now() + timedelta(days=days_ahead)
    
    # Persian day names
    persian_days = {
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه', 
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه',
        'Saturday': 'شنبه',
        'Sunday': 'یکشنبه'
    }
    
    day_name_english = target_date.strftime('%A')
    day_name_persian = persian_days.get(day_name_english, day_name_english)
    
    return {
        "target_date": target_date.strftime('%Y-%m-%d'),
        "day_of_week": day_name_english,
        "day_of_week_persian": day_name_persian,
        "formatted_date": target_date.strftime('%Y-%m-%d'),
        "human_readable": f"{day_name_persian} {target_date.strftime('%Y/%m/%d')}",
        "days_from_today": days_ahead,
        "is_future": days_ahead > 0,
        "is_past": days_ahead < 0,
        "is_today": days_ahead == 0
    }
