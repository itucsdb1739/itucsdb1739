from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from flask import current_app
from itupass.models import Department, Lecture, LectureSchedule


def get_database():
    from itupass import get_db
    return get_db(current_app)


LECTURES_CODES_URL = "http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php"
LECTURES_URL = "http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php?fb={code}"


def parse_lectures_data():
    # Get list of departments in system
    current_year = datetime.now().year + 1
    departments_obj = Department.filter(limit=100)
    departments = []
    for department in departments_obj:
        departments.append(department.code)
    if not departments:
        print("No departments in system!")
    # Get list of lecture codes:
    r = requests.get(LECTURES_CODES_URL)
    bs = BeautifulSoup(r.text, "html.parser")
    codes = [option.text.strip() for option in bs.find("select", {"name": "bolum"}).findAll("option")[1:]]
    # @TODO check for updates
    for code in codes:
        r = requests.get(LECTURES_URL.format(code=code))
        r.encoding = "windows-1254"
        bs = BeautifulSoup(r.text, "html.parser")
        for lecture in bs.findAll("tr", {"onmouseover": "this.bgColor='#D4E6FD'"}):
            lecture_details = lecture.findAll("td")
            # Check if lecture is for supported departments
            lecture_deps = [dep.strip() for dep in lecture_details[11].text.split(',')]
            if set(departments).isdisjoint(lecture_deps):
                continue
            # Check if lecture already exists
            db_lecture = Lecture.filter(crn=int(lecture_details[0].text), year=current_year)
            if not db_lecture:
                print("Adding lecture {lecture}".format(lecture=lecture_details[2].text.strip()))
                # Add new lecture
                new_lecture = Lecture(
                    crn=int(lecture_details[0].text),
                    code=lecture_details[1].text,
                    name=lecture_details[2].text.strip(),
                    instructor=lecture_details[3].text.strip(),
                    year=current_year
                )
                new_lecture = new_lecture.save()
                for dep in lecture_deps:
                    new_lecture.add_department(dep)
                db_lecture.append(new_lecture)
            # Check for lecture schedules
            db_lecture = db_lecture[0]
            db_schedules = db_lecture.get_schedules()
            if not db_schedules:
                print("Adding schedules for lecture {pk}:{lecture}".format(pk=db_lecture.pk, lecture=db_lecture.name))
                # no schedules, add
                schedule_days = lecture_details[5].text.strip().split(' ')
                schedule_hours = lecture_details[6].text.strip().split(' ')
                for item in lecture_details[4].findAll('br'):
                    item.replace_with(' ')
                schedule_buildings = lecture_details[4].text.strip().split(' ')
                schedule_rooms = lecture_details[7].text.strip().split(' ')
                for schedule_day in schedule_days:
                    schedule_hour = schedule_hours[schedule_days.index(schedule_day)]
                    start_time = schedule_hour.split('/')[0]
                    end_time = schedule_hour.split('/')[1]
                    if len(start_time) == 4:
                        start_time = start_time[:2] + ':' + start_time[2:] + ':00'
                    else:
                        start_time = None
                    if len(end_time) == 4:
                        end_time = end_time[:2] + ':' + end_time[2:] + ':00'
                    else:
                        end_time = None
                    db_schedule = LectureSchedule(
                        lecture=db_lecture.pk,
                        building=schedule_buildings[schedule_days.index(schedule_day)],
                        room=schedule_rooms[schedule_days.index(schedule_day)],
                        day_of_week=schedule_day,
                        start_time=start_time,
                        end_time=end_time
                    )
                    db_schedule = db_schedule.save()
