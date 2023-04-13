from aat import app, db
from aat.models import User, Teacher, Student, Department, Programme, Difficulty, Tag

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

DIFFICULTIES = [1, 2, 3, 4, 5]

TAGS = ["Algorithm", "Data Structure", "Software", "Machine Learning", "Artificial Intelligence", "DevOps", "Design Pattern"]



def addAccount(email, password, firstname, lastname, id_num, teacher=False, programme=""):
    user = User.query.filter_by(email=email, password=password, firstname=firstname, lastname=lastname).first()
    if not user:
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
            student.programme_id = Programme.query.filter_by(name=programme).first().id
            db.session.add(student)
        db.session.commit()

def addDepartment(name, abbreviation, programmes=[]):
    department = Department.query.filter_by(name=name, abbreviation=abbreviation).first()
    if not department:
        department = Department(name=name, abbreviation=abbreviation)
        for pg in programmes:
            programme = Programme(name=pg["name"])
            department.programmes.append(programme)
        db.session.add(department)
        db.session.commit()

def addDifficulty(level):
    difficulty = Difficulty.query.filter_by(level=level).first()
    if not difficulty:
        difficulty = Difficulty(level=level)
        db.session.add(difficulty)
        db.session.commit()

def addTag(tag_name):
    tag = Tag.query.filter_by(tag=tag_name, official=True).first()
    if not tag:
        print("adding" + tag_name)
        tag = Tag(tag=tag_name, official=True)
        db.session.add(tag)
        db.session.commit()

with app.app_context():
    for department in DEPARTMENTS:
        addDepartment(department["name"], department["abbreviation"], department["programmes"])
    for ac in ACCOUNTS:
        addAccount(ac[0], ac[1], ac[2], ac[3], ac[4], ac[5], ac[6])
    for diff_lv in DIFFICULTIES:
        addDifficulty(diff_lv)
    for tag_name in TAGS:
        addTag(tag_name)
