from datetime import datetime
from datetime import timezone


def nws_to_iso_time(nws_time: str):
    """ Convert time from NWS to ISO 8601 format"""
    utc_time = (str(datetime.fromisoformat(nws_time).astimezone(timezone.utc))
                .replace(" ", ""))  # Convert time to UTC
    iso_time = f"{utc_time[:-6]}Z"  # Remove +00:00 and add Z to signify Zulu time
    return iso_time
