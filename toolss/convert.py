from datetime import datetime
from binancess.const import TIME_FORMAT

def timestampms_to_utc(timestamp: int, format=TIME_FORMAT):
    return datetime.utcfromtimestamp(timestamp // 1000).strftime(format)
