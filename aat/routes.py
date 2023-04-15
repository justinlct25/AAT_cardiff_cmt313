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
		course = Course(number=form.number.data, name=form.name.data, description=form.description.data, programme_id=form.programme_id.data)
		db.session.add(course)
		db.session.flush()
		user.teacher.courses.append(course)
		db.session.commit()
		flash('Course created successfully!')
		return redirect(url_for('courses'))
	return render_template('courses.html', courses=courses, form=form)

@app.route("/course/<int:course_id>", methods=['GET'])
def course(course_id):
    user = User.query.get(current_user.id)
    course = Course.query.get(course_id)
    # print(user.teacher)
    # is_student = any(student.id == current_user.id for student in course.programme.students)
    return render_template('course.html', course=course)

@app.route("/template/select/<int:course_id>", methods=['GET'])
def template_select(course_id):
    course = Course.query.get(course_id)
    templates = AssessmentTemplate.query.all()
    return render_template('template_select.html', course=course, templates=templates)

@app.route("/template/new/<int:course_id>", methods=['GET', 'POST'])
def template_new(course_id):
    user = User.query.get(current_user.id)
    teacher = Teacher.query.get(user.teacher.id)
    course = Course.query.get(course_id) if not course_id == 0 else None
    form = AssessmentTemplateForm()
    if form.validate_on_submit() and current_user.teacher:
        template = AssessmentTemplate(creator_id=current_user.id, name=form.name.data, description=form.description.data, can_retake=form.can_retake.data, limit_time=form.limit_time.data, duration=form.duration.data)
        template.difficulty = Difficulty.query.get(form.difficulty_id.data)
        tag = Tag.query.get(form.tag_id.data)
        template.tags.append(tag)
        if course: 
          template.used_in_courses.append(course)
        teacher.created_templates.append(template)
        db.session.add(template)
        db.session.commit()
        flash("New assessment is added")
        # if not course_id == 0: # been here from templates
        return redirect(url_for('template_edit', template_id=template.id, course_id=course_id))
        # else:
    return render_template("template_new.html", course=course, form=form)

@app.route("/template/view/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_view(template_id, course_id):
    template = AssessmentTemplate.query.get(template_id)
    course = Course.query.get(course_id) if not course_id == 0 else None # course_id==0 means this route isnt get into through adding new assessment within a course
    return render_template("template_view.html", course=course, template=template, mc_id_char=MC_ID_CHAR)

@app.route("/template/edit/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit(template_id, course_id):
    template = AssessmentTemplate.query.get(template_id)
    course = Course.query.get(course_id)
    form = AssessmentTemplateForm()
    form.description.data = template.description
    form.can_retake.data = template.can_retake
    if request.method == 'POST' and form.validate():
        template.name = form.name.data
        template.description = form.description.data
        template.can_retake = form.can_retake.data
        template.limit_time = form.limit_time.data
        template.duration = form.duration.data
        template.difficulty = Difficulty.query.get(form.difficulty_id.data)
        tag = Tag.query.get(form.tag_id.data)
        template.tags = []
        template.tags.append(tag)
        db.session.commit()
        return redirect(url_for("template_view", template_id=template_id, course_id=course_id))
    return render_template("template_edit.html", course=course, template=template, form=form, mc_id_char=MC_ID_CHAR)

@app.route("/template/edit/question/st/new/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit_short_question_new(template_id, course_id):
    user = User.query.get(current_user.id)
    teacher = Teacher.query.get(user.teacher.id)
    template = AssessmentTemplate.query.get(template_id)
    form = StQuestionForm()
    if form.validate_on_submit():
        question = StQuestion(creator_id=current_user.id, question=form.question.data, correct_ans=form.correct_ans.data, feedback_correct=form.feedback_correct.data, feedback_wrong=form.feedback_wrong.data)
        db.session.add(question)
        template.st_questions.append(question)
        teacher.created_st_questions.append(question)
        db.session.commit()
        return redirect(url_for("template_view", template_id=template_id, course_id=course_id))
    return render_template("question_st_new.html", template=template, form=form)

@app.route("/template/edit/question/mc/new/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit_multiple_choice_question_new(template_id, course_id):
    user = User.query.get(current_user.id)
    teacher = Teacher.query.get(user.teacher.id)
    template = AssessmentTemplate.query.get(template_id)
    form = McQuestionForm()
    if form.validate_on_submit():
        question = McQuestion(creator_id=current_user.id, question=form.question.data, feedback=form.feedback.data, choice_1=form.choice_1.data, choice_2=form.choice_2.data, choice_3=form.choice_3.data, choice_4=form.choice_4.data, choice_feedback_1=form.choice_feedback_1.data, choice_feedback_2=form.choice_feedback_2.data, choice_feedback_3=form.choice_feedback_3.data, choice_feedback_4=form.choice_feedback_4.data, correct_choice_id=MC_CHAR_ID[form.correct_choice.data])
        db.session.add(question)
        template.mc_questions.append(question)
        teacher.created_mc_questions.append(question)
        db.session.commit()
        return redirect(url_for("template_view", template_id=template_id, course_id=course_id))
    return render_template("question_mc_new.html", template=template, form=form)

# @app.route("/template/edit/question/mc/new/num_choices<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
# def template_edit_multiple_choice_question_new_num_choices(template_id, course_id):
#     template = AssessmentTemplate.query.get(template_id)
#     mcChoicesNumberForm = McChoicesNumberForm()
#     creator = User.query.get(template.creator_id)
#     creator_name = creator.firstname + " " + creator.lastname
#     if mcChoicesNumberForm.validate_on_submit():
#       mcQuestionForm = McQuestionForm()
#       numChoices = mcChoicesNumberForm.num_choices.data
#       mcQuestionForm.choices.min_entries = numChoices
#       mcQuestionForm.choices.max_entries = numChoices
#       # mcQuestionForm.options = FieldList(FormField(McChoiceForm), min_entries=numChoices, max_entries=numChoices)
#       mcQuestionForm.correct_answer.choices = [(i, f'Choice {i+1}') for i in range(numChoices)]
#       return render_template("question_mc_new_question.html", template=template, template_creator=creator_name, form=mcQuestionForm)
#     return render_template("question_mc_new_num_choices.html", template=template, template_creator=creator_name, form=mcChoicesNumberForm)

@app.route("/assessment/new/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def assessment_new(template_id, course_id):
    course = Course.query.get(course_id)
    template = AssessmentTemplate.query.get(template_id)
    form = AssessmentForm()
    if form.validate_on_submit() and current_user.teacher:
        assessment = Assessment(course_id=course_id, is_formative=form.is_formative.data, start_at=form.start_at.data, end_at=form.end_at.data)
        assessment.template = template
        db.session.add(assessment)
        db.session.flush()
        course.assessments.append(assessment)
        db.session.commit()
        return redirect(url_for("assessment", assessment_id=assessment.id))
    return render_template("assessment_new.html", course=course, template=template, form=form)

@app.route("/assessment/<int:assessment_id>", methods=['GET'])
def assessment(assessment_id):
    assessment = Assessment.query.get(assessment_id)
    return render_template("assessment.html", assessment=assessment)

@app.route("/assessments", methods=['GET'])
def assessments():
   return render_template('assessments.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500