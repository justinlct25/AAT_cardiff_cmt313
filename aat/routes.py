from flask import render_template, flash, request, redirect, url_for
from aat import app, db
from aat.models import *
from aat.forms import *
from flask_login import login_user, logout_user, current_user, login_required
import random


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if current_user:
       user = User.query.get(current_user.id)
    return render_template("index.html", user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user is not None and user.verify_password(form.password.data):
        login_user(user)
        flash('You\'ve successfully logged in,'+' '+ current_user.email +'!')
        return redirect(url_for('home'))
      flash('Invalid email or password.')
    return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
  logout_user()
  flash('You\'re now logged out. Thanks for your visit!')
  return redirect(url_for('home'))

@app.route("/register", methods=['GET','POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    # user = User(username=form.username.data, password=form.password.data, icon=f'default_{random.randint(0,9)}.png')
    # db.session.add(user)
    # db.session.commit()
    flash('Registration successful!')
    return redirect(url_for('registered'))
  return render_template('register.html',title='Register', form=form)

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    if current_user.is_authenticated:
        is_owner = user_id == current_user.id
    else:
        is_owner = False   
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', is_owner=is_owner, user=user)

@app.route("/courses", methods=['GET', 'POST'])
def courses():
   user = User.query.get(current_user.id)
   if user.student: courses = user.student.courses if user.student.courses else []
   else: courses = user.teacher.courses if user.teacher.courses else []
   form = CourseForm()
   if form.validate_on_submit() and current_user.teacher:
      course = Course(name=form.name.data, description=form.description.data)
      db.session.add(course)
      db.session.flush()
      user.teacher.courses.append(course)
      db.session.commit()
      flash('Course created successfully!')
      return redirect(url_for('courses'))
   return render_template('courses.html', courses=courses, form=form)

@app.route("/assessments", methods=['GET'])
def assessments():
   return render_template('assessments.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500