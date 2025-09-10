from django import template
from datetime import datetime, timezone

register = template.Library()

@register.filter
def minutes_to_hours(mins):
    try:
        return f"{(int(mins) or 0)/60:.1f} h"
    except Exception:
        return "0.0 h"
    
@register.filter
def epoch_to_date(epoch_seconds):
    try:
        e = int(epoch_seconds)
        if e <= 0: return "-"
        dt = datetime.fromtimestamp(e, tz=timezone.utc).astimezone()
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return "-"