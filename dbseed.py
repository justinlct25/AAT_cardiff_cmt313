from aat import app, db
from aat.models import User, Teacher, Student, Department, Programme

ACCOUNTS = [
        ["andy@cardiff.ac.uk", "andy1010", "Tsang An", "Lee", "22011528", True, ""],
        ["ivor@cardiff.ac.uk", "ivor1010", "Ivor", "Mandekich", "1867157", True, ""], 
        ["mike@cardiff.ac.uk", "mike1010", "Ziye", "Zhang", "21095796", True, ""],
        ["kp@cardiff.ac.uk", "kp1010", "Khai Pong", "Teoh", "22085771", False, "Computer Science"],
        ["wan@cardiff.ac.uk", "wan1010", "Guowen", "Ye", "22080190", False, "Software Engineering"],
        ["justin@cardiff.ac.uk", "justin1010", "Chun Ting Justin", "Lo", "22075165", False, "Data Science"]
    ]

DEPARTMENTS = [
    {
        "name": "School of Computer Science and Informatics",
        "abbreviation": "COMSC",
        "programmes": [
            {"name": "Computer Science"},
            {"name": "Software Engineering"},
            {"name": "Data Science"}
        ]
    }
]

def addAccount(email, password, firstname, lastname, id_num, teacher=False, programme=""):
    user = User(email=email, password=password, firstname=firstname, lastname=lastname)
    db.session.add(user)
    db.session.flush()
    if teacher:
        teacher = Teacher(teacher_num=id_num)
        teacher.user = user
        db.session.add(teacher)
    else:
        student = Student(student_num=id_num)
        student.user = user
        # programme = Programme.query.filter_by(abbreviation=programme).first()
        # print(programme)
        student.programme_id = Programme.query.filter_by(name=programme).first().id
        db.session.add(student)
    db.session.commit()

def addDepartment(name, abbreviation, programmes=[]):
    department = Department(name=name, abbreviation=abbreviation)
    for pg in programmes:
        programme = Programme(name=pg["name"])
        department.programmes.append(programme)
    db.session.add(department)
    db.session.commit()

with app.app_context():
    for department in DEPARTMENTS:
        addDepartment(department["name"], department["abbreviation"], department["programmes"])
    for ac in ACCOUNTS:
        addAccount(ac[0], ac[1], ac[2], ac[3], ac[4], ac[5], ac[6])

# with app.app_context():
#     pg = Programme.query.filter_by(name="COMSC").first()
#     print(pg)