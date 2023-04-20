from flask import render_template, flash, request, redirect, url_for
from aat import app, db
from aat.models import *
from aat.forms import *
from flask_login import login_user, logout_user, current_user, login_required
from aat.helper import update_template_total_marks

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user is not None and user.verify_password(form.password.data):
        login_user(user)
        flash('You\'ve successfully logged in,'+' '+ current_user.email +'!', category="success")
        return redirect(url_for('dashboard'))
      flash('Invalid email or password.', category="danger")
    return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
  logout_user()
  flash('You\'re now logged out. Thanks for your visit!', category="success")
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

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template('dashboard.html')

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    if current_user.is_authenticated:
        is_owner = user_id == current_user.id
    else:
        is_owner = False   
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', is_owner=is_owner, user=user)

# Andy part

@app.route("/faq", methods=['GET'])
def faq():
    return render_template('pages-faq.html')

@app.route("/contact", methods=['GET'])
def contact():
    return render_template('pages-contact.html')

@app.route("/questions", methods=['GET'])
def questions():
    mc_questions = McQuestion.query.order_by(McQuestion.id.asc()).paginate(page=1, per_page=5)
    st_questions = StQuestion.query.order_by(StQuestion.id.asc()).paginate(page=1, per_page=5)
    return render_template('question_bank.html', mc_questions=mc_questions, st_questions=st_questions)

@app.route("/questions/add", methods=["GET", "POST"])
def questions_add():
    return render_template('question_bank_add.html')

# Andy part end

@app.route("/courses", methods=['GET', 'POST'])
def courses():
	user = User.query.get(current_user.id)
	if user.student: courses = user.student.programme.courses if user.student.programme.courses else []
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
	return render_template('courses.html', courses=courses, form=form, user=user)

@app.route("/course/<int:course_id>", methods=['GET'])
def course(course_id):
    user = User.query.get(current_user.id)
    course = Course.query.get(course_id)
    assessment_attempts = []
    if user.student:
        for assessment in course.assessments:
            attempts = StudentAttemptStatus.query.filter_by(student_id=user.student.id, assessment=assessment)
            latest_attempt = attempts.order_by(StudentAttemptStatus.id.desc()).first()
            # if latest_attempt: # of not then no attempt yet
            assessment_attempts.append(latest_attempt) # attempt_id=0: havnt attempt yet
    print(assessment_attempts)
    return render_template('course.html', course=course, user=user, datetime=datetime, assessment_attempts=assessment_attempts)

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
        flash("Created new assessment templated")
        # if not course_id == 0: # been here from templates
        return redirect(url_for('template', template_id=template.id, course_id=course_id))
        # else:
    return render_template("template_new.html", course=course, form=form)

@app.route("/template/view/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template(template_id, course_id):
    template = AssessmentTemplate.query.get(template_id)
    course = Course.query.get(course_id) if not course_id == 0 else None # course_id==0 means this route isnt get into through adding new assessment within a course
    return render_template("template.html", course=course, template=template, mc_id_char=MC_ID_CHAR)

@app.route("/template/edit/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit(template_id, course_id):
    template = AssessmentTemplate.query.get(template_id)
    course = Course.query.get(course_id)
    form = AssessmentTemplateForm()
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
        flash("Edited assessment template")
        return redirect(url_for("template", template_id=template_id, course_id=course_id))
    return render_template("template_edit.html", course=course, template=template, form=form, mc_id_char=MC_ID_CHAR)

@app.route("/template/edit/question/st/new/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit_short_question_new(template_id, course_id):
    user = User.query.get(current_user.id)
    course = Course.query.get(course_id)
    teacher = Teacher.query.get(user.teacher.id)
    template = AssessmentTemplate.query.get(template_id)
    form = StQuestionForm()
    if form.validate_on_submit():
        question = StQuestion(creator_id=current_user.id, question=form.question.data, correct_ans=form.correct_ans.data, feedback_correct=form.feedback_correct.data, feedback_wrong=form.feedback_wrong.data, marks=form.marks.data)
        db.session.add(question)
        template.st_questions.append(question)
        teacher.created_st_questions.append(question)
        update_template_total_marks(template)
        db.session.commit()
        return redirect(url_for("template", template_id=template_id, course_id=course_id))
    st_questions = StQuestion.query.order_by(StQuestion.id.asc()).paginate(page=1, per_page=5)
    return render_template("question_st_new.html", template=template, form=form, st_questions=st_questions, course=course)

@app.route("/template/edit/question/mc/new/<int:template_id>/<int:course_id>", methods=['GET', 'POST'])
def template_edit_multiple_choice_question_new(template_id, course_id):
    user = User.query.get(current_user.id)
    course = Course.query.get(course_id)
    teacher = Teacher.query.get(user.teacher.id)
    template = AssessmentTemplate.query.get(template_id)
    form = McQuestionForm()
    if form.validate_on_submit():
        question = McQuestion(creator_id=current_user.id, question=form.question.data, feedback=form.feedback.data, choice_1=form.choice_1.data, choice_2=form.choice_2.data, choice_3=form.choice_3.data, choice_4=form.choice_4.data, choice_feedback_1=form.choice_feedback_1.data, choice_feedback_2=form.choice_feedback_2.data, choice_feedback_3=form.choice_feedback_3.data, choice_feedback_4=form.choice_feedback_4.data, correct_choice_id=MC_CHAR_ID[form.correct_choice.data], marks=form.marks.data)
        db.session.add(question)
        template.mc_questions.append(question)
        teacher.created_mc_questions.append(question)
        update_template_total_marks(template)
        db.session.commit()
        return redirect(url_for("template", template_id=template_id, course_id=course_id))
    mc_questions = McQuestion.query.order_by(McQuestion.id.asc()).paginate(page=1, per_page=5)
    return render_template("question_mc_new.html", template=template, form=form, mc_questions=mc_questions, course=course, mc_id_char=MC_ID_CHAR)

@app.route("/template/edit/question/st/select/<int:question_id>/<int:template_id>/<int:course_id>", methods=['POST'])
def template_edit_short_question_select(question_id, template_id, course_id):
    st_question = StQuestion.query.get(question_id)
    course = Course.query.get(course_id)
    template = AssessmentTemplate.query.get(template_id)
    template.st_questions.append(st_question)
    update_template_total_marks(template)
    db.session.commit()
    return redirect(url_for('template', template_id=template.id, course_id=course.id))

@app.route("/template/edit/question/mc/select/<int:question_id>/<int:template_id>/<int:course_id>", methods=['POST'])
def template_edit_multiple_choice_question_select(question_id, template_id, course_id):
    mc_question = McQuestion.query.get(question_id)
    course = Course.query.get(course_id)
    template = AssessmentTemplate.query.get(template_id)
    template.mc_questions.append(mc_question)
    update_template_total_marks(template)
    db.session.commit()
    return redirect(url_for('template', template_id=template.id, course_id=course.id))

@app.route("/template/edit/question/st/delete/<int:question_id>/<int:template_id>/<int:course_id>", methods=['POST'])
def template_edit_short_question_delete(question_id, template_id, course_id):
    st_question = StQuestion.query.get(question_id)
    course = Course.query.get(course_id)
    template = AssessmentTemplate.query.get(template_id)
    if st_question in template.st_questions:
      template.st_questions.remove(st_question)
      update_template_total_marks(template)
      db.session.commit()
    return redirect(url_for('template', template_id=template.id, course_id=course.id))

@app.route("/template/edit/question/mc/delete/<int:question_id>/<int:template_id>/<int:course_id>", methods=['POST'])
def template_edit_multiple_choice_question_delete(question_id, template_id, course_id):
    mc_question = McQuestion.query.get(question_id)
    course = Course.query.get(course_id)
    template = AssessmentTemplate.query.get(template_id)
    if mc_question in template.mc_questions:
      template.mc_questions.remove(mc_question)
      update_template_total_marks(template)
      db.session.commit()
    return redirect(url_for('template', template_id=template.id, course_id=course.id))

@app.route("/template/confirm/<int:template_id>/<int:course_id>", methods=['POST'])
def template_confirm(template_id, course_id):
    template = AssessmentTemplate.query.get(template_id)
    template.is_confirmed = True
    update_template_total_marks(template)
    db.session.commit()
    return redirect(url_for("template", template_id=template_id, course_id=course_id))

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
    user = User.query.get(current_user.id)
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
        return redirect(url_for("assessment_view", assessment_id=assessment.id))
    return render_template("assessment_new.html", user = user, course=course, template=template, form=form)

@app.route("/assessment/view/<int:assessment_id>", methods=['GET'])
def assessment_view(assessment_id):
    user = User.query.get(current_user.id)
    assessment = Assessment.query.get(assessment_id)
    return render_template("assessment_view.html", user=user, assessment=assessment, mc_id_char=MC_ID_CHAR)

@app.route("/assessment/attempt/<int:assessment_id>/<int:attempt_id>", methods=['GET', 'POST'])
def assessment_attempt(assessment_id, attempt_id=0):
    user = User.query.get(current_user.id)
    assessment = Assessment.query.get(assessment_id)
    mc_forms = [McAnswerForm(obj=question) for question in assessment.template.mc_questions]
    st_forms = [StAnswerForm(obj=question) for question in assessment.template.st_questions]
    mc_answers, st_answers = [], []
    if attempt_id == 0: # student first attempt / re-attempt the assessment
      student_attempt_status = StudentAttemptStatus(student_id=user.student.id)
      student_attempt_status.assessment = assessment
      db.session.add(student_attempt_status)
      user.student.attempts.append(student_attempt_status)
      db.session.commit()
      attempt_id = student_attempt_status.id
      mc_answers = [0] * len(assessment.template.mc_questions)
      st_answers = [0] * len(assessment.template.st_questions)
    else: # student continues his/her assessment attempt
      student_attempt_status = StudentAttemptStatus.query.get(attempt_id)
      for question in assessment.template.mc_questions:
          mc_answer = db.session.query(McStudentAns).filter_by(attempt_id=student_attempt_status.id, question_id=question.id).first()
          mc_answers.append(mc_answer)
      for question in assessment.template.st_questions:
          st_answer = db.session.query(StStudentAns).filter_by(attempt_id=student_attempt_status.id, question_id=question.id).first()
          st_answers.append(st_answer)
    return render_template("assessment_attempt.html", user=user, assessment=assessment, mc_forms=mc_forms, st_forms=st_forms, mc_id_char=MC_ID_CHAR, attempt_id=attempt_id, mc_answers=mc_answers, st_answers=st_answers)

@app.route("/assessment/attempt/mc/<int:attempt_id>/<int:question_id>", methods=['GET', 'POST'])
def assessment_attempt_mc(attempt_id, question_id):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    question = McQuestion.query.get(question_id)
    form = McAnswerForm()
    if form.validate_on_submit():
      answer_choice_id = MC_CHAR_ID[form.answer.data]
      answer_is_correct = question.correct_choice_id == answer_choice_id
      marks = question.marks if answer_is_correct else 0
      mc_answer = McStudentAns.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
      if mc_answer: # student already submitted an answer before
          mc_answer.answer_choice_id = answer_choice_id
          mc_answer.is_correct = answer_is_correct
          mc_answer.marks = marks
          flash("Edited MC question")
      else: # student have not submitted an answer before
          mc_answer = McStudentAns(attempt_id=attempt.id, question_id=question_id, answer_choice_id=answer_choice_id, is_correct=answer_is_correct, marks=marks)
          db.session.add(mc_answer)
          attempt.mc_answers.append(mc_answer)
          flash("Answered Multiple Choice question")
      db.session.commit()
      return redirect(url_for("assessment_attempt", assessment_id=attempt.assessment.id, attempt_id=attempt_id))
    flash("Failed to answer Multiple Choice question")
    return redirect(url_for("assessment_attempt", assessment_id=attempt.assessment.id, attempt_id=attempt_id))

@app.route("/assessment/attempt/st/<int:attempt_id>/<int:question_id>", methods=['GET', 'POST'])
def assessment_attempt_st(attempt_id, question_id):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    question = StQuestion.query.get(question_id)
    form = StAnswerForm()
    if form.validate_on_submit():
      answer = form.answer.data
      answer_is_correct = question.correct_ans == answer
      marks = question.marks if answer_is_correct else 0
      st_answer = StStudentAns.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
      if st_answer: # student already submitted an answer before
          st_answer.answer = answer
          st_answer.is_correct = answer_is_correct
          st_answer.marks = marks
          flash("Edited Short question")
      else: # student have not submitted an answer before
          st_answer = StStudentAns(attempt_id=attempt.id, question_id=question_id, answer=answer, is_correct=answer_is_correct, marks=marks)
          db.session.add(st_answer)
          attempt.st_answers.append(st_answer)
          flash("Answered Short question")
      db.session.commit()
      return redirect(url_for("assessment_attempt", assessment_id=attempt.assessment.id, attempt_id=attempt_id))
    flash("Failed to answer MC question")
    return redirect(url_for("assessment_attempt", assessment_id=attempt.assessment.id, attempt_id=attempt_id))

@app.route("/assessment/submit/<int:attempt_id>", methods=['POST'])
def assessment_submit(attempt_id):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    attempt_total_marks = 0
    for answer in attempt.mc_answers:
        attempt_total_marks += answer.marks
    for answer in attempt.st_answers:
        attempt_total_marks += answer.marks
    attempt.total_marks = attempt_total_marks
    attempt.is_submitted = True
    attempt.attempted_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('assessment_result', attempt_id=attempt_id))

@app.route("/assessment/result/<int:attempt_id>", methods=['GET'])
def assessment_result(attempt_id):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    assessment_total_marks = 0
    for question in attempt.assessment.template.mc_questions:
        assessment_total_marks += question.marks
    for question in attempt.assessment.template.st_questions:
        assessment_total_marks += question.marks
    mc_answers, st_answers = [], []
    for question in attempt.assessment.template.mc_questions:
        mc_answer = db.session.query(McStudentAns).filter_by(attempt_id=attempt_id, question_id=question.id).first()
        mc_answers.append(mc_answer)
    for question in attempt.assessment.template.st_questions:
        st_answer = db.session.query(StStudentAns).filter_by(attempt_id=attempt_id, question_id=question.id).first()
        st_answers.append(st_answer)
    return render_template("assessment_result.html", attempt=attempt, assessment=attempt.assessment, assessment_total_marks=assessment_total_marks, mc_answers=mc_answers, st_answers=st_answers, mc_id_char=MC_ID_CHAR)

@app.route("/assessment/results/<int:assessment_id>", methods=['GET'])
def assessment_results(assessment_id):
    assessment = Assessment.query.get(assessment_id)
    programme = assessment.course.programme
    student_attempt_records = []
    student_attempt_times = []
    for student in programme.students:
        attempts = StudentAttemptStatus.query.filter_by(student_id=student.id, assessment=assessment)
        record = attempts.order_by(StudentAttemptStatus.id.desc()).first()
        if record:
          if assessment.is_formative:
              student_attempt_times.append(len(attempts.all()))
          student_attempt_records.append(record)
    print(student_attempt_records)
    return render_template("assessment_results.html", programme=programme, assessment=assessment, student_attempt_records=student_attempt_records, student_attempt_times=student_attempt_times)


@app.route("/statistic/<int:assessment_id>", methods=['GET'])    
def statistic(assessment_id):
    data = StudentAttemptStatus.query.filter_by(assessment_id=assessment_id)
    return render_template("statistic", data=data)


@app.route("/assessments", methods=['GET'])
def assessments():
   return render_template('assessments.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
