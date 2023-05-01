from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, DateField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Regexp
from aat.models import *
from aat import app
from flask import flash
from sqlalchemy import inspect

MC_ID_CHAR = {
  1: "A",
  2: "B", 
  3: "C", 
  4: "D"
} 

MC_CHAR_ID = {
  "A": 1,
  "B": 2,
  "C": 3,
  "D": 4
}

class RegistrationForm(FlaskForm):
  username = StringField('Username',validators=[DataRequired(),Regexp('^[a-z0-9]{6,14}$',message='Your username should be between 6 and 12 characters long, and can only contain lowercase letters.')])
  password = PasswordField('Password',validators=[DataRequired(), EqualTo('confirm_password', message='Passwords do not match. Try again')])
  email = StringField('Email', validators=[DataRequired()])
  confirm_password = PasswordField('Password',validators=[DataRequired()])
  submit = SubmitField('Register')

  def validate_username(self, username):
    print(username)
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      flash('Username already exist. Please choose a different one.')
      raise ValidationError('Username already exist. Please choose a different one.')

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Login')

class CourseForm(FlaskForm):
  number = StringField('Number', validators=[DataRequired()])
  name = StringField('Name', validators=[DataRequired()])
  description = StringField('Description')
  submit = SubmitField('Submit')
  with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("programme"):
      programme_choices = []
    else:
      programme_choices = [(programme.id, programme.name) for programme in Programme.query.all()]
  programme_id = SelectField('Programme', choices=programme_choices)

class AssessmentTemplateForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  description = StringField('Description')
  can_retake = BooleanField("Retake")
  limit_time = BooleanField("Time")
  duration = IntegerField("Duration", default=60)
  submit = SubmitField('Add')
  with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("difficulty") or not inspector.has_table("tag"):
      difficulty_choices, tag_choices = [], []
    else:
      difficulty_choices = [(difficulty.id, difficulty.level) for difficulty in Difficulty.query.all()]
      tag_choices = [(tag.id, tag.tag) for tag in Tag.query.all()]
  difficulty_id = SelectField('Difficulty', choices=difficulty_choices)
  tag_id = SelectField('Tag', choices=tag_choices)

  # def __init__(self, template=None, **kwargs):
  #   super().__init__(**kwargs)
  #   if template:
  #     self.name.default = template.name
  #     self.description.default = template.description
  #     self.can_retake.default = template.can_retake
  #     self.limit_time.default = template.limit_time
  #     self.duration.default = template.duration
  #     self.difficulty_id.default = template.difficulty.id
  #     self.tag_id.default = template.tags[0].id
  #     self.process(obj=template)

class AssessmentForm(FlaskForm):
  is_formative = BooleanField("Formative", default=False)
  start_at = DateField("StartDate")
  end_at = DateField("EndDate")
  submit = SubmitField('Add Assessment')

class StQuestionForm(FlaskForm):
  question = StringField("Question", validators=[DataRequired()])
  correct_ans = StringField("Answer", validators=[DataRequired()])
  feedback_correct = StringField("Feedback for Correct Answer")
  feedback_wrong = StringField("Feedback for Wrong Answer")
  marks = IntegerField("Marks", default=1)
  difficulty = IntegerField("Difficulty")

# class McChoicesNumberForm(FlaskForm):
#   num_choices = IntegerField('Number of Choices')
#   submit = SubmitField('New Multiple Choices Question')

# class McChoiceForm(FlaskForm):
#   choice = StringField('Choice')
#   correct = BooleanField('Is Correct Answer')

# class McQuestionForm(FlaskForm):
#   question = StringField('Question')
#   options = FieldList(FormField(McChoiceForm), min_entries=0, max_entries=10)
#   correct_answer = RadioField('Correct Answer', choices=[], coerce=int)

class McQuestionForm(FlaskForm):
  question = StringField("Question", validators=[DataRequired(message='Please enter a question')])
  feedback = StringField("Feedback")
  choice_1 = StringField("Choice 1", validators=[DataRequired(message='Please enter choice 1')])
  choice_2 = StringField("Choice 2", validators=[DataRequired(message='Please enter choice 2')])
  choice_3 = StringField("Choice 3", validators=[DataRequired(message='Please enter choice 3')])
  choice_4 = StringField("Choice 4", validators=[DataRequired(message='Please enter choice 4')])
  choice_feedback_1 = StringField("Feedback")
  choice_feedback_2 = StringField("Feedback")
  choice_feedback_3 = StringField("Feedback")
  choice_feedback_4 = StringField("Feedback")
  correct_choice = SelectField("Correct Choice Id", choices=["A", "B", "C", "D"])
  marks = IntegerField("Marks", default=1,)
  difficulty = IntegerField("Difficulty")

class StAnswerForm(FlaskForm):
  answer = StringField("Answer")
  submit = SubmitField('Save')

class McAnswerForm(FlaskForm):
  answer = SelectField("Answer", choices=["A", "B", "C", "D"])
  submit = SubmitField('Save')

class AttemptFeedbackForm(FlaskForm):
  feedback = StringField("Feedback", validators=[DataRequired()])
  submit = SubmitField('Save')
