from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from itupass.models import Department, Lecture


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
    for code in codes:
        r = requests.get(LECTURES_URL.format(code=code))
        bs = BeautifulSoup(r.text, "html.parser")
        lectures = []
        for lecture in bs.findAll("tr", {"onmouseover": "this.bgColor='#D4E6FD'"}):
            lecture_details = lecture.findAll("td")
            # Check if lecture is for supported departments
            lecture_deps = [dep.strip() for dep in lecture_details[11].text.split(',')]
            if set(departments).isdisjoint(lecture_deps):
                continue
            # Check if lecture already exists
            if Lecture.filter(crn=int(lecture_details[0].text), year=current_year):
                continue
            # Add new lecture
            new_lecture = Lecture(
                crn=int(lecture_details[0].text),
                code=lecture_details[1].text,
                name=,
                instructor='',
                # @TODO
                year=current_year
            )
