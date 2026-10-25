from datetime import date

from fastapi import APIRouter, HTTPException, Path, Query

from app.core.config import settings
from app.schemas.holiday import Holiday, HolidayCheck
from app.services.holiday_service import HolidayAPIError, get_public_holidays, holidays_near

router = APIRouter(prefix="/holidays", tags=["holidays"])

CountryCode = Query(default=None, min_length=2, max_length=2, description="ISO country code, e.g. US")


@router.get("/check", response_model=HolidayCheck)
def check_date(
    day: date = Query(alias="date", description="Due date to check, YYYY-MM-DD"),
    country: str | None = CountryCode,
    window_days: int = Query(default=3, ge=0, le=14),
):
    """Is a due date on, or within `window_days` of, a public holiday?"""
    country = (country or settings.default_country_code).upper()
    try:
        nearby = holidays_near(day, country, window_days)
    except HolidayAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return HolidayCheck(
        date=day,
        country_code=country,
        is_holiday=any(h.date == day for h in nearby),
        window_days=window_days,
        nearby_holidays=nearby,
    )


@router.get("/{year}", response_model=list[Holiday])
def list_holidays(year: int = Path(ge=1975, le=2075), country: str | None = CountryCode):
    """All public holidays for a year and country, from Nager.Date."""
    country = (country or settings.default_country_code).upper()
    try:
        return get_public_holidays(year, country)
    except HolidayAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
