from datetime import date

from pydantic import BaseModel


class Holiday(BaseModel):
    date: date
    local_name: str
    name: str
    country_code: str


class HolidayCheck(BaseModel):
    date: date
    country_code: str
    is_holiday: bool
    window_days: int
    nearby_holidays: list[Holiday]
