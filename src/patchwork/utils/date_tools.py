from datetime import datetime


def now_stamp():
    return datetime.utcnow().isoformat() + "Z"


def old_school_day_name():
    name = datetime.utcnow().strftime("%A")
    return name
