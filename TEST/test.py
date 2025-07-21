import time
from datetime import datetime, timedelta
import calendar

def getDaysPeriod():
    today = datetime.now()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    try:
        same_day_last_month = last_day_previous_month.replace(day=today.day)
    except ValueError:
        same_day_last_month = last_day_previous_month
    return (today - same_day_last_month).days



day_period = getDaysPeriod()
print(f"Today: {datetime.now().strftime('%Y-%m-%d')}")
print(f"Period of time in days: {day_period} days")
