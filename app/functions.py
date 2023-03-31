import datetime

def microsec_to_datetime(microsec):
    diff = datetime.timedelta(microseconds=microsec)
    days = diff.days
    
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    latency = ""
    
    if days > 0:
        latency += str(days) + " days "
    if hours > 0:
        latency += str(hours) + " hours "
    if minutes > 0:
        latency += str(minutes) + " minutes "
    if seconds > 0:
        latency += str(seconds) + " seconds "
    
    return latency
    