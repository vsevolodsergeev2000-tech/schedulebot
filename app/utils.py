from datetime import datetime
import pytz
from config import settings

def parse_datetime(datetime_str: str, timezone: str = None) -> datetime:
    """
    Преобразует строку вида "DD.MM.YYYY HH:MM" в объект datetime с указанной временной зоной.
    По умолчанию используется зона из настроек.
    """
    if timezone is None:
        timezone = settings.TIMEZONE
    try:
        naive_dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
    except ValueError:
        raise ValueError("Неверный формат. Используйте DD.MM.YYYY HH:MM")
    tz = pytz.timezone(timezone)
    return tz.localize(naive_dt)