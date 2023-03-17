from aat import app, db
from aat.models import User, Teacher, Student
from werkzeug.security import generate_password_hash

ACCOUNTS = [
        ["andy@cardiff.ac.uk", "andy1010", "Tsang An", "Lee", "22011528", True],
        ["ivor@cardiff.ac.uk", "ivor1010", "Ivor", "Mandekich", "1867157", True], 
        ["mike@cardiff.ac.uk", "mike1010", "Ziye", "Zhang", "21095796", True],
        ["kp@cardiff.ac.uk", "kp1010", "Khai Pong", "Teoh", "22085771", False],
        ["wan@cardiff.ac.uk", "wan1010", "Guowen", "Ye", "22080190", False],
        ["justin@cardiff.ac.uk", "justin1010", "Chun Ting Justin", "Lo", "22075165", False]
    ]


def addAccount(email, password, firstname, lastname, id_num, teacher=False):
    user = User(email=email, password=generate_password_hash(password), firstname=firstname, lastname=lastname)
    db.session.add(user)
    db.session.flush()
    if teacher:
        teacher = Teacher(teacher_num=id_num)
        teacher.user = user
        db.session.add(teacher)
    else:
        student = Student(student_num=id_num)
        student.user = user
        db.session.add(student)
    db.session.commit()

with app.app_context():
    for ac in ACCOUNTS:
        addAccount(ac[0], ac[1], ac[2], ac[3], ac[4], ac[5])