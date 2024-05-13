import time

class TimeoutException(Exception):
    pass

def time_limited_execution(end_time):
    if time.time() > end_time:
        raise TimeoutException("Time limit exceeded")
    return False