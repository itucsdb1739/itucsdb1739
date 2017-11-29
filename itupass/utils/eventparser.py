from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from itupass.models import Event, EventCategory


MONTH = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

MATCH_TIME_RANGE = re.compile("^([0-9]*)\s([A-Z]1?[a-z]*)\s([0-9]*)\s\(Time\s([0-9]*:[0-9]*)\s-\s([0-9]*:[0-9]*)\)$")
MATCH_TIME_SINGLE = re.compile("^([0-9]*)\s([A-Z]1?[a-z]*)\s([0-9]*)\s\(Time\s([0-9]*:[0-9]*)\)$")
MATCH_DATE_WITH_END_M = re.compile("^([0-9]*)\s([A-Z]*[a-z]*)\-([0-9]*)\s([A-Z]*[a-z]*)\s([0-9]*)$")
MATCH_DATE_TRIPLE_RANGE = re.compile("^([0-9]*)\-([0-9]*)\-([0-9]*)\s([A-Z]*[a-z]*)\s([0-9]*)$")
MATCH_DATE_RANGE = re.compile("^([0-9]*)\-([0-9]*)\s([A-Z]*[a-z]*)\s([0-9]*)$")
MATCH_SINGLE_DATE = re.compile("^([0-9]*)\s([A-Z]*[a-z]*)\s([0-9]*)$")


def parse_academic_calendar():
    CALENDAR_URL = "http://www.sis.itu.edu.tr/eng/calendar/calendar{year}/lisanstakvimEN.htm"
    category = EventCategory.get(slug='academic-calendar')
    r = requests.get(CALENDAR_URL.format(year=datetime.now().year + 1))
    bs = BeautifulSoup(r.text, "html.parser")
    events = bs.findAll('table')[3].findAll('tr')[2:]
    for event in events:
        summary = event.findAll('span')[0].text.replace('\xa0', ' ').replace('\r', '').replace(
                '\n', '').replace('\t', '')
        page_date = event.findAll('span')[1].text.replace('\xa0', ' ').replace('\r', '').replace(
                '\n', '').replace('\t', '').replace('  ', ' ').strip()
        # get and remove time
        start_datetime = None
        end_datetime = None
        if MATCH_TIME_RANGE.match(page_date):
            day, month, year, start_time, end_time = MATCH_TIME_RANGE.match(page_date).groups()
            start_hour, start_minute = start_time.split(':')
            end_hour, end_minute = end_time.split(':')
            start_datetime = datetime(
                day=int(day), month=MONTH[month], year=int(year), hour=int(start_hour), minute=int(start_minute)
            )
            end_datetime = datetime(
                day=int(day), month=MONTH[month], year=int(year), hour=int(end_hour), minute=int(end_minute)
            )
        elif MATCH_TIME_SINGLE.match(page_date):
            day, month, year, start_time = MATCH_TIME_SINGLE.match(page_date).groups()
            start_hour, start_minute = start_time.split(':')
            start_datetime = datetime(
                day=int(day), month=MONTH[month], year=int(year), hour=int(start_hour), minute=int(start_minute)
            )
        elif MATCH_DATE_WITH_END_M.match(page_date):
            day, month, second_day, second_month, year = MATCH_DATE_WITH_END_M.match(page_date).groups()
            start_datetime = datetime(day=int(day), month=MONTH[month], year=int(year))
            end_datetime = datetime(day=int(second_day), month=MONTH[second_month], year=int(year))
        elif MATCH_DATE_TRIPLE_RANGE.match(page_date):
            day, _, second_day, month, year = MATCH_DATE_TRIPLE_RANGE.match(page_date).groups()
            start_datetime = datetime(day=int(day), month=MONTH[month], year=int(year))
            end_datetime = datetime(day=int(second_day), month=MONTH[month], year=int(year))
        elif MATCH_DATE_RANGE.match(page_date):
            day, second_day, month, year = MATCH_DATE_RANGE.match(page_date).groups()
            start_datetime = datetime(day=int(day), month=MONTH[month], year=int(year))
            end_datetime = datetime(day=int(second_day), month=MONTH[month], year=int(year))
        elif MATCH_SINGLE_DATE.match(page_date):
            day, month, year = MATCH_SINGLE_DATE.match(page_date).groups()
            start_datetime = datetime(day=int(day), month=MONTH[month], year=int(year))
        else:
            # @TODO log warning
            print("[ERROR] Date parsing: {date}".format(date=page_date))
            continue
        if not Event.filter(summary=summary, date=start_datetime):
            new_event = Event(summary=summary, date=start_datetime, end_date=end_datetime, category=category.pk)
            new_event.save()
            # @TODO log success
