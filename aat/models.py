# Justin, I let you to take full charge of this file, thanks!

from datetime import datetime
from aat import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from aat.associations import *

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=True, default="")
    hashed_password=db.Column(db.String(128))
    firstname = db.Column(db.String(50), unique=True, nullable=False)
    lastname = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.Text, nullable=True, default="user_default_1.png")
    about = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def password(self):
      raise AttributeError('Password is not readable.')

    @password.setter
    def password(self,password):
      self.hashed_password=generate_password_hash(password)

    def verify_password(self,password):
      return check_password_hash(self.hashed_password, password)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class Teacher(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user = db.relationship('User', secondary=user_teacher_association_table, backref=db.backref('teacher', uselist=False), uselist=False) # one-to-one
  courses = db.relationship('Course', secondary=teacher_courses_association_table, backref='teacher')
  created_templates = db.relationship('AssessmentTemplate', secondary=teacher_templates_association_table, backref=db.backref('creator', uselist=False))
  created_st_questions = db.relationship('StQuestion', secondary=teacher_st_questions_association_table, backref=db.backref('creator', uselist=False))
  created_mc_questions = db.relationship('McQuestion', secondary=teacher_mc_questions_association_table, backref=db.backref('creator', uselist=False))
  teacher_num = db.Column(db.String(10), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  programme_id = db.Column(db.Integer, db.ForeignKey('programme.id'))
  user = db.relationship('User', secondary=user_student_association_table, backref=db.backref('student', uselist=False), uselist=False) # one-to-one
  courses = db.relationship('Course', secondary=student_courses_association_table, backref='student') # many-to-many
  attempts = db.relationship('StudentAttemptStatus', secondary=student_attempts_association_table, backref=db.backref('student', uselist=False))
  student_num = db.Column(db.String(10), nullable=False)
  start_yr = db.Column(db.DateTime)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Department(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60), nullable=False)
  abbreviation = db.Column(db.String(10))
  programmes = db.relationship('Programme', backref=db.backref('department', uselist=False), lazy=True) # one-to-many

class Programme(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(60), nullable=False)
  department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
  students = db.relationship('Student', backref='programme', lazy=True) # one-to-many
  courses = db.relationship('Course', backref='programme', lazy=True) # one-to-many

class Course(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  programme_id = db.Column(db.Integer, db.ForeignKey('programme.id'), nullable=False)
  number = db.Column(db.String(10), nullable=False)
  name = db.Column(db.String(100), unique=True, nullable=False)
  description = db.Column(db.String(1000), default="")
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  assessments = db.relationship('Assessment', backref='course', lazy=True) # one-to-many

class Assessment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
  template = db.relationship('AssessmentTemplate', secondary=assessment_template_association_table, backref='assessment', uselist=False) 
  is_formative = db.Column(db.Boolean, default=False)
  start_at = db.Column(db.DateTime, nullable=False)
  end_at = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class AssessmentTemplate(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  creator_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
  name = db.Column(db.String(100), nullable=False)
  description = db.Column(db.String(200), default="")
  can_retake = db.Column(db.Boolean, default=False)
  limit_time = db.Column(db.Boolean, default=False)
  duration = db.Column(db.Integer, default=60)
  is_confirmed = db.Column(db.Boolean, default=False)
  total_marks = db.Column(db.Integer, default=0)
  difficulty = db.relationship('Difficulty', secondary=template_difficulty_association_table, backref='template', uselist=False) 
  tags = db.relationship('Tag', secondary=template_tags_association_table, backref='template')
  mc_questions = db.relationship('McQuestion', secondary=template_mcquestions_association_table, backref='template')
  fb_questions = db.relationship('FbQuestion', secondary=template_fbquestions_association_table, backref='template')
  st_questions = db.relationship('StQuestion', secondary=template_stquestions_association_table, backref='template')
  used_in_courses = db.relationship('Course', secondary=template_courses_association_table, backref='template')
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Tag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tag = db.Column(db.String(50), unique=True, nullable=False)
  official = db.Column(db.Boolean, default=False)

class Difficulty(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  level = db.Column(db.Integer, nullable=False, default=1)

class McQuestion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question = db.Column(db.String(100), nullable=False)
  multiple = db.Column(db.Boolean, default=False)
  feedback = db.Column(db.String(100), default="")
  difficulty = db.relationship('Difficulty', secondary=mcquestion_difficulty_association_table, backref='mc_question', uselist=False) 
  tags = db.relationship('Tag', secondary=mcquestion_tags_association_table, backref='mc_question')
  choices = db.relationship('Choice', backref='mc_question', lazy=True) # one-to-many
  creator_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
  choice_1 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_2 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_3 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_4 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  correct_choice_id = db.Column(db.Integer, nullable=False) # easy version of multiple choice without using choice table
  choice_feedback_1 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_feedback_2 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_feedback_3 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  choice_feedback_4 = db.Column(db.String(200)) # easy version of multiple choice without using choice table
  marks = db.Column(db.Integer, default=1)

class StQuestion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question = db.Column(db.String(500), nullable=False)
  correct_ans = db.Column(db.String(100), nullable=False)
  feedback_correct = db.Column(db.String(200), default="")
  feedback_wrong = db.Column(db.String(200), default="")
  difficulty = db.relationship('Difficulty', secondary=stquestion_difficulty_association_table, backref='st_question', uselist=False) 
  tags = db.relationship('Tag', secondary=stquestion_tags_association_table, backref='st_question')
  creator_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
  marks = db.Column(db.Integer, default=1)

class Choice(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question_id = db.Column(db.Integer, db.ForeignKey('mc_question.id'))
  choice = db.Column(db.String(50), nullable=False)
  correct_ans = db.Column(db.Boolean, default=False)
  marks = db.Column(db.Integer, default=1)

class FbQuestion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question = db.Column(db.String(500), nullable=False)
  feedback = db.Column(db.String(100), default="")
  difficulty = db.relationship('Difficulty', secondary=fbquestion_difficulty_association_table, backref='fb_question', uselist=False) 
  tags = db.relationship('Tag', secondary=fbquestion_tags_association_table, backref='fb_question')
  blanks = db.relationship('Blank', backref='fb_question', lazy=True) # one-to-many
  
class Blank(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question_id = db.Column(db.Integer, db.ForeignKey('fb_question.id'))
  correct_ans = db.Column(db.String(50), nullable=False)
  marks = db.Column(db.Integer, default=1)

class StudentAttemptStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
  assessment = db.relationship('Assessment', secondary=assessment_status_association_table, backref='assessment_status', uselist=False) 
  attempts = db.Column(db.Integer, default=0)
  total_marks = db.Column(db.Integer, default=0)
  attempted_at = db.Column(db.DateTime)
  is_submitted = db.Column(db.Boolean, default=False)
  result_is_confirmed = db.Column(db.Boolean, default=False)
  feedback = db.Column(db.String(200), default="")
  mc_answers = db.relationship('McStudentAns', secondary=attempt_mc_answers_association_table, backref=db.backref('attempt', uselist=False))
  st_answers = db.relationship('StStudentAns', secondary=attempt_st_answers_association_table, backref=db.backref('attempt', uselist=False))

class McStudentAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  attempt_id = db.Column(db.Integer, db.ForeignKey('student_attempt_status.id'))
  question_id = db.Column(db.Integer, db.ForeignKey('mc_question.id'))
  selected_choices = db.relationship('Choice', secondary=mcans_choices_association_table, backref='mc_ans')
  answer_choice_id = db.Column(db.Integer, nullable=False)  # easy version of multiple choice without using choice table
  is_correct = db.Column(db.Boolean, default=False)
  marks = db.Column(db.Integer, default=0)
  creator_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

class StStudentAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  attempt_id = db.Column(db.Integer, db.ForeignKey('student_attempt_status.id'))
  question_id = db.Column(db.Integer, db.ForeignKey('st_question.id'))
  answer = db.Column(db.String(100), nullable=False)
  is_correct = db.Column(db.Boolean, default=False)
  marks = db.Column(db.Integer, default=0)

class FbStudentAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  attempt_id = db.Column(db.Integer, db.ForeignKey('student_attempt_status.id'))
  question_id = db.Column(db.Integer, db.ForeignKey('fb_question.id'))
  blank_answers = db.relationship('BlankAns', backref='fb_student_ans', lazy=True)
  marks = db.Column(db.Integer, default=0)

class BlankAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ans_id = db.Column(db.Integer, db.ForeignKey('fb_student_ans.id'))
  blank_id = db.Column(db.Integer, db.ForeignKey('blank.id'))
  student_ans = db.Column(db.String(50))





