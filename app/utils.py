from datetime import datetime
import pytz
from config import settings

MOSCOW_TZ = pytz.timezone("Europe/Moscow")


def parse_moscow_to_utc(datetime_str: str) -> datetime:
    """
    Преобразует строку с датой/временем в формате DD.MM.YYYY HH:MM,
    считая её московским временем, в UTC datetime.
    """
    try:
        naive_dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
    except ValueError:
        raise ValueError("Неверный формат. Используйте DD.MM.YYYY HH:MM")

    moscow_dt = MOSCOW_TZ.localize(naive_dt)
    utc_dt = moscow_dt.astimezone(pytz.UTC)
    return utc_dt

def format_moscow_from_utc(utc_dt: datetime) -> str:
    """Конвертирует UTC время в московское и возвращает строку ДД.ММ.ГГГГ ЧЧ:ММ MSK"""
    moscow_dt = utc_dt.astimezone(MOSCOW_TZ)
    return moscow_dt.strftime("%d.%m.%Y %H:%M") + " MSK"