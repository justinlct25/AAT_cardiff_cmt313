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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @property
    def password(self):
      raise AttributeError('Password is not readable.')

    @password.setter
    def password(self,password):
      self.hashed_password=generate_password_hash(password)

    def verify_password(self,password):
      return check_password_hash(self.hashed_password,password)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class Teacher(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user = db.relationship('User', secondary=user_teacher_association_table, backref='teacher', uselist=False) # one-to-one
  modules = db.relationship('Module', secondary=teacher_modules_association_table, backref='teacher')
  teacher_num = db.Column(db.String(10), nullable=False)

class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user = db.relationship('User', secondary=user_student_association_table, backref='student', uselist=False) # one-to-one
  modules = db.relationship('Module', secondary=student_modules_association_table, backref='student') # many-to-many
  student_num = db.Column(db.String(10), nullable=False)

class Module(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), unique=True, nullable=False)
  description = db.Column(db.String(500), default="")
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  assessments = db.relationship('Assessment', backref='module', lazy=True) # one-to-many

class Assessment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
  template = db.relationship('AssessmentTemplate', secondary=assessment_template_association_table, backref='assessment') 
  is_formative = db.Column(db.Boolean, default=False)
  start_at = db.Column(db.DateTime, nullable=False)
  end_at = db.Column(db.DateTime, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class AssessmentTemplate(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  creator_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
  name = db.Column(db.String(15), unique=True, nullable=False)
  description = db.Column(db.String(200), default="")
  retake = db.Column(db.Boolean, default=False)
  duration = db.Column(db.Integer)
  difficulty = db.relationship('Difficulty', secondary=template_difficulty_association_table, backref='template', uselist=False) 
  tags = db.relationship('Tag', secondary=template_tags_association_table, backref='template')
  mc_questions = db.relationship('McQuestion', secondary=template_mcquestions_association_table, backref='template')
  fb_questions = db.relationship('FbQuestion', secondary=template_fbquestions_association_table, backref='template')
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Tag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tag = db.Column(db.String(10), unique=True, nullable=False)
  official = db.Column(db.Boolean, default=False)

class Difficulty(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  difficulty = db.Column(db.Integer, nullable=False, default=1)

class McQuestion(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  question = db.Column(db.String(100), nullable=False)
  multiple = db.Column(db.Boolean, default=False)
  feedback = db.Column(db.String(100), default="")
  difficulty = db.relationship('Difficulty', secondary=mcquestion_difficulty_association_table, backref='mc_question', uselist=False) 
  tags = db.relationship('Tag', secondary=mcquestion_tags_association_table, backref='mc_question')
  choices = db.relationship('Choice', backref='mc_question', lazy=True) # one-to-many

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

class StudentAssessmentStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
  assessment = db.relationship('Assessment', secondary=assessment_status_association_table, backref='assessment_status', uselist=False) 
  attempts = db.Column(db.Integer, default=0)
  total_marks = db.Column(db.Integer, default=0)
  attempted_at = db.Column(db.DateTime)

class McStudentAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  status_id = db.Column(db.Integer, db.ForeignKey('student_assessment_status.id'))
  question_id = db.Column(db.Integer, db.ForeignKey('mc_question.id'))
  selected_choices = db.relationship('Choice', secondary=mcans_choices_association_table, backref='mc_ans')
  marks = db.Column(db.Integer, default=0)

class FbStudentAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  status_id = db.Column(db.Integer, db.ForeignKey('student_assessment_status.id'))
  question_id = db.Column(db.Integer, db.ForeignKey('fb_question.id'))
  blank_answers = db.relationship('BlankAns', backref='fb_student_ans', lazy=True)
  marks = db.Column(db.Integer, default=0)

class BlankAns(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ans_id = db.Column(db.Integer, db.ForeignKey('fb_student_ans.id'))
  blank_id = db.Column(db.Integer, db.ForeignKey('blank.id'))
  student_ans = db.Column(db.String(50))

