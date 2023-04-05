import datetime
from decimal import Decimal

day_secs = 24 * 60 * 60

def seconds_to_time(secs):
    diff = datetime.timedelta(seconds=secs)
    days = diff.days
    
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return time_to_str(days, hours, minutes, seconds)

def avg_to_time(secs):
    if secs == None:
        return None
    secs = Decimal(secs)
    
    days, day_reminder = divmod(secs, day_secs)
    hours, remainder = divmod(day_reminder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return time_to_str(days, hours, minutes, seconds)    

def time_to_str(days, hours, minutes, seconds):
    result = ""
    
    if days > 0:
        result += str(days) + " days "
    if hours > 0:
        result += str(hours) + " hours "
    if minutes > 0:
        result += str(minutes) + " minutes "
    if seconds > 0:
        result += str(seconds) + " seconds "
    
    return result

def convert_to_datetime(obj):
    return obj.strftime('%Y-%m-%d %H:%M:%S')
    