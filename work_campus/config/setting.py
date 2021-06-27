import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE_PATH, 'db')
SCHOOL_DATA = os.path.join(DB, "campus.pk")
PROGRAM_DATA = os.path.join(DB, "programs.pk")
COURSE_DATA = os.path.join(DB, "course.pk")
STUDENT_DATA = os.path.join(DB, "student.pk")
STAFF_DATA = os.path.join(DB, "staff.pk")
LECTURER_DATA = os.path.join(DB, "lecturer.pk")