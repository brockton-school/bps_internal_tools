from datetime import datetime, time

from bps_internal_tools.services.settings import get_system_tzinfo

def should_ask_reason_and_return_time(user_type: str) -> str:
    """Return whether the kiosk should ask for a reason/return time."""

# Helper for preventing reason when end of day sign out
def should_ask_reason_and_return_time(user_type):
    current_time = datetime.now(get_system_tzinfo()).time()
    cutoff_time = time(14, 0)  # 2:00 PM in the configured timezone
    if user_type == "Staff" and current_time > cutoff_time:
        return "false"  # Don't ask for reason/return time
    return "true"  # Ask for reason/return time