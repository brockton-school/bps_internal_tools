"""Helpers for storing and updating lightweight application settings."""

from datetime import datetime
from typing import List, Optional

import pytz

from bps_internal_tools.extensions import db
from bps_internal_tools.models import AppSetting

DEFAULT_TIMEZONE = "America/Vancouver"
_TIMEZONE_SETTING_KEY = "system_timezone"


def _get_setting_row(key: str) -> Optional[AppSetting]:
    return db.session.get(AppSetting, key)


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    row = _get_setting_row(key)
    if row is None or row.value is None:
        return default
    return row.value


def set_setting(key: str, value: Optional[str]) -> None:
    session = db.session
    row = _get_setting_row(key)
    now = datetime.utcnow()
    if row is None:
        row = AppSetting(key=key, value=value, updated_at=now)
        session.add(row)
    else:
        row.value = value
        row.updated_at = now
    session.commit()


def get_system_timezone() -> str:
    value = get_setting(_TIMEZONE_SETTING_KEY, DEFAULT_TIMEZONE) or DEFAULT_TIMEZONE
    try:
        pytz.timezone(value)
    except pytz.UnknownTimeZoneError:
        return DEFAULT_TIMEZONE
    return value


def get_system_tzinfo():
    return pytz.timezone(get_system_timezone())


def list_supported_timezones() -> List[str]:
    timezones = list(pytz.common_timezones)
    if DEFAULT_TIMEZONE in timezones:
        timezones.remove(DEFAULT_TIMEZONE)
    timezones.insert(0, DEFAULT_TIMEZONE)
    return timezones


def set_system_timezone(timezone_name: str) -> str:
    if not timezone_name:
        raise ValueError("Timezone is required.")
    try:
        pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError as exc:  # pragma: no cover - defensive path
        raise ValueError(f"'{timezone_name}' is not a recognized timezone.") from exc
    set_setting(_TIMEZONE_SETTING_KEY, timezone_name)
    return timezone_name