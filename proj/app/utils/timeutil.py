from time import mktime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from dateutil import parser
from pytz import timezone, UTC
from proj.app import settings

IST = timezone("Asia/Kolkata")
EST_EDT = timezone("US/Eastern")
CST_CDT = timezone("US/Central")
MST_MDT = timezone("US/Mountain")
PST_PDT = timezone("US/Pacific")
Arizona = timezone('US/Arizona')
Alaska = timezone('US/Alaska')
GMT_BST = timezone('Europe/London')
CET_CEST = timezone('CET')


timezones = {
    'IST': IST,
    'UTC': UTC,
    'EST-EDT': EST_EDT,
    'CST-CDT': CST_CDT,
    'MST-MDT': MST_MDT,
    'PST-PDT': PST_PDT,
    'Arizona': Arizona,
    'Alaska': Alaska,
    'GMT-BST': GMT_BST,
    'CET-CEST': CET_CEST
}


def get_app_timezone():
    server_timezone = getattr(settings, 'SERVER_TIMEZONE', None)
    return timezones.get(server_timezone, UTC)


def to_aware(date_time, tz=None):
    is_datetime = isinstance(date_time, datetime)
    is_date = isinstance(date_time, date)
    if not is_date and not is_datetime:
        try:
            date_time = parser.parse(date_time)
            is_datetime = True
        except (ValueError, TypeError):
            raise ValueError("expected a valid date or datetime")
    if not is_datetime or getattr(date_time, 'tzinfo', None) is None:  # naive
        date_time = datetime.fromtimestamp(mktime(date_time.timetuple()))
        try:
            # according to the settings or supplied tz
            settings_tz = get_app_timezone()
            date_time = (tz or settings_tz).localize(date_time)
        except AttributeError:
            raise ValueError("invalid timezone specified")
    return date_time


def to_utc(date_time, tz=None):
    if not getattr(date_time, 'tzinfo', None):
        date_time = UTC.normalize(to_aware(date_time, tz=tz))
    elif not date_time.tzinfo == UTC:
        date_time = UTC.normalize(date_time)
    return date_time


def timenow():
    timemachine_time = getattr(settings, 'TIME_MACHINE_TIME', None)
    if not timemachine_time:
        return to_utc(datetime.now())
    else:
        return to_utc(parser.parse(timemachine_time))


def time_to_next_day(datetime_object):
    tomorrow = datetime_object + relativedelta(days=1)
    tomorrow_starts = datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=tomorrow.tzinfo)
    time_remaining = tomorrow_starts - datetime_object
    time_remaining_in_seconds = time_remaining.total_seconds()
    delta = relativedelta(seconds=time_remaining_in_seconds)
    return delta, time_remaining_in_seconds


def timestamp_to_aware(timestamp, tz=None):
    tz = tz or get_app_timezone()
    return datetime.fromtimestamp(timestamp, tz)


def stringify_day(date_time):
    if not isinstance(date_time, datetime):
        date_time = parser.parse(date_time)
    return date_time.strftime('%d-%m-%y')
