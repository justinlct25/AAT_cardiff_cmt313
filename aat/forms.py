from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Regexp
from aat.models import User
from flask import flash


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
  email = StringField('Email',validators=[DataRequired()])
  password = PasswordField('Password',validators=[DataRequired()])
  submit = SubmitField('Login')