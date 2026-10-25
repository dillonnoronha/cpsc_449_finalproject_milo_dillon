"""Client for the public Nager.Date holiday API (https://date.nager.at)."""
from datetime import date, timedelta

import httpx

from app.core.config import settings
from app.schemas.holiday import Holiday


class HolidayAPIError(Exception):
    pass


def get_public_holidays(year: int, country_code: str) -> list[Holiday]:
    url = f"{settings.nager_date_base_url}/PublicHolidays/{year}/{country_code.upper()}"
    try:
        response = httpx.get(url, timeout=10)
    except httpx.HTTPError as exc:
        raise HolidayAPIError(f"Could not reach Nager.Date: {exc}") from exc

    # Nager.Date returns 404 for an unknown country code and 204 when it has no data
    if response.status_code in (204, 404):
        return []
    if response.status_code != 200:
        raise HolidayAPIError(f"Nager.Date returned HTTP {response.status_code}")

    return [
        Holiday(
            date=item["date"],
            local_name=item["localName"],
            name=item["name"],
            country_code=item["countryCode"],
        )
        for item in response.json()
    ]


def holidays_near(day: date, country_code: str, window_days: int = 3) -> list[Holiday]:
    """Public holidays within `window_days` of `day` (handles windows crossing a new year)."""
    start, end = day - timedelta(days=window_days), day + timedelta(days=window_days)
    holidays: list[Holiday] = []
    for year in range(start.year, end.year + 1):
        holidays.extend(get_public_holidays(year, country_code))
    return [h for h in holidays if start <= h.date <= end]
