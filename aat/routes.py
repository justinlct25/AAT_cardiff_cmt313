from flask import render_template, flash, request, redirect, url_for, Response
from aat import app, db
from aat.models import *
from aat.forms import *
from flask_login import login_user, logout_user, current_user, login_required
from aat.helper import update_template_total_marks
from io import TextIOWrapper, StringIO
from sqlalchemy import func
from urllib.parse import unquote

import random, csv, io


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

@app.route("/view", methods=['GET'])
def view():
    return render_template('view.html')

@app.route("/faq", methods=['GET'])
def faq():
    return render_template('pages-faq.html')

@app.route("/contact", methods=['GET'])
def contact():
    return render_template('pages-contact.html')

@app.route("/question-bank/questions", methods=['GET'])
def questions():
    tags = Tag.query.all()
    tag_counts = []
    for tag in tags:
        st_count = StQuestion.query.filter(StQuestion.tags.contains(tag)).count()
        mc_count = McQuestion.query.filter(McQuestion.tags.contains(tag)).count()
        tag_counts.append((tag.tag, st_count + mc_count))

    categories = Tag.query.order_by(Tag.id.asc())
    mc_questions = McQuestion.query.order_by(McQuestion.id.asc()).paginate(page=request.args.get('mc_page', 1, type=int), per_page=5)
    st_questions = StQuestion.query.order_by(StQuestion.id.asc()).paginate(page=request.args.get('st_page', 1, type=int), per_page=5)
    question_types = [
    {'name': 'Multiple Choice', 'id': 'multiple_choice', 'description': 'This question type allows respondents to select one answer choice from a list of options. The options are usually presented in a list format with a radio button or checkbox next to each option.'},
    {'name': 'Short Answer', 'id': 'short_answer', 'description': 'This question type allows respondents to provide a brief, free-form text response to a prompt or question. The answer length is typically limited to a specific number of characters or words.'},
    {'name': 'Essay', 'id': 'essay', 'description': 'This question type requires respondents to provide a longer, free-form text response to a prompt or question. Unlike a short answer question, an essay question typically does not have a specific word or character limit.'},
    {'name': 'True/False', 'id': 'true_false', 'description': 'This question type requires respondents to indicate whether a statement or question is true or false. This is typically done by selecting a radio button or checkbox next to the "true" or "false" option.'},
    {'name': 'Ranking', 'id': 'ranking', 'description': 'This question type requires respondents to order a list of options according to their preference, importance, or another criteria. The options are usually presented in a list format and the respondent is asked to drag and drop or use arrows to rearrange the order.'},
    {'name': 'Likert Scale', 'id': 'likert_scale', 'description': 'This question type requires respondents to indicate their level of agreement or disagreement with a statement or question on a scale. The scale typically ranges from "strongly agree" to "strongly disagree" and is presented with radio buttons or checkboxes.'},
    {'name': 'Dropdown', 'id': 'dropdown', 'description': 'This question type presents a list of options in a dropdown menu format, and respondents must select one of the options from the menu. This question type is often used when there are too many options to display on a single page.'},
    {'name': 'Matrix', 'id': 'matrix', 'description': 'This question type presents a matrix or grid format, where respondents are asked to rate or evaluate multiple items on a set of predefined criteria. The rows of the matrix represent the items to be evaluated, and the columns represent the criteria.'},
    {'name': 'Matching', 'id': 'matching', 'description': 'This question type requires respondents to match items from one list to another. The items are usually presented in a list format, with one list containing the options to be matched and the other containing the matching criteria.'},
    {'name': 'File Upload', 'id': 'file_upload', 'description': 'This question type allows respondents to upload a file or document as their response to a question or prompt. This question type is often used when respondents are asked to provide evidence or examples to support their answers.'}
]
    return render_template('question_bank.html', 
                           mc_questions=mc_questions, st_questions=st_questions, 
                           categories=categories,
                           question_types=question_types,
                           tag_counts=tag_counts)

@app.route("/question-bank/add/multiple-choice", methods=["GET", "POST"])
def mc_questions_add():
    form = McQuestionForm()
    
    if form.validate_on_submit():
        category = request.args.get('category')
        print(category)
        tag = Tag.query.filter_by(tag=category).first_or_404()
        print(tag)
        question = McQuestion(creator_id=current_user.id, question=form.question.data, feedback=form.feedback.data, choice_1=form.choice_1.data, choice_2=form.choice_2.data, choice_3=form.choice_3.data, choice_4=form.choice_4.data, choice_feedback_1=form.choice_feedback_1.data, choice_feedback_2=form.choice_feedback_2.data, choice_feedback_3=form.choice_feedback_3.data, choice_feedback_4=form.choice_feedback_4.data, correct_choice_id=MC_CHAR_ID[form.correct_choice.data], marks=form.marks.data,
        tags=[tag])
        db.session.add(question)
        db.session.commit()
        flash('Question created successfully!', category="success")
        return redirect(url_for('questions'))
    return render_template('add_mc_question.html', form=form)


@app.route("/question-bank/add/short-answer", methods=["GET", "POST"])
def st_questions_add():
    form = StQuestionForm()
    if form.validate_on_submit():
        category = request.args.get('category')
        print(category)
        tag = Tag.query.filter_by(tag=category).first_or_404()
        print(tag)
        question = StQuestion(creator_id=current_user.id, question=form.question.data, correct_ans=form.correct_ans.data, feedback_correct=form.feedback_correct.data, feedback_wrong=form.feedback_wrong.data, marks=form.marks.data,
        tags=[tag])
        db.session.add(question)
        db.session.commit()
        flash('Question created successfully!', category="success")
        return redirect(url_for('questions'))
    return render_template('add_st_question.html', form=form)

@app.route("/category/add", methods=["GET", "POST"])
def category_add():
    return redirect(url_for('questions', _anchor='category'))


# Route to delete a multiple choice question
@app.route('/delete-mc-question/<int:question_id>')
def delete_mc_question(question_id):
    question = McQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', category='success')
    return redirect(url_for('questions'))

# Route to delete a short question
@app.route('/delete-st-question/<int:question_id>')
def delete_st_question(question_id):
    question = StQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', category='success')
    return redirect(url_for('questions'))



@app.route('/edit-mc-question/<int:question_id>', methods=['GET', 'POST'])
def edit_mc_question(question_id):
    question = McQuestion.query.get_or_404(question_id)
    form = McQuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        question.correct_choice_id = MC_CHAR_ID[form.correct_choice.data]
        db.session.commit()
        flash('Question updated successfully!', category='success')
        return redirect(url_for('questions'))
    return render_template('edit_mc_question.html', form=form, question=question)

@app.route('/edit-st-question/<int:question_id>', methods=['GET', 'POST'])
def edit_st_question(question_id):
    question = StQuestion.query.get_or_404(question_id)
    form = StQuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question updated successfully!', category='success')
        return redirect(url_for('questions'))
    return render_template('edit_st_question.html', form=form, question=question)


# Test the edit or delete for multiple questions
# Route to edit multiple choice questions
@app.route('/edit-mc-questions', methods=['GET', 'POST'])
def edit_mc_questions():
    ids = request.args.get('ids').split(',')
    questions = McQuestion.query.filter(McQuestion.id.in_(ids)).all()
    form = McQuestionForm(obj=questions)
    if form.validate_on_submit():
        for question in questions:
            form.populate_obj(question)
            question.correct_choice_id = MC_CHAR_ID[form.correct_choice.data]
            db.session.commit()
        flash('Questions updated successfully!', category='success')
        return redirect(url_for('questions'))
    return render_template('edit_mc_questions.html', form=form, questions=questions, ids=ids)

# Route to delete multiple choice questions
@app.route('/delete-mc-questions', methods=['GET', 'POST'])
def delete_mc_questions():
    ids = request.args.get('ids').split(',')
    for question_id in ids:
        question = McQuestion.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
    flash('Questions deleted successfully!', category='success')
    return redirect(url_for('questions'))


@app.route('/add_category', methods=['POST', 'GET'])
def add_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        category = Tag(tag=category_name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', category='success')
        return redirect(url_for('questions'))
    return render_template('add_category.html')


@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files['csv-file']
        if file:
            csv_file = TextIOWrapper(file, encoding='utf-8')
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # skip header row
            for row in csv_reader:
                question_type = row[0]
                if question_type == 'mc':
                    question = McQuestion(
                        question=row[1],
                        multiple=bool(row[2]),
                        feedback=row[3],
                        choice_1=row[4],
                        choice_2=row[5],
                        choice_3=row[6],
                        choice_4=row[7],
                        correct_choice_id=int(row[8]),
                        choice_feedback_1=row[9],
                        choice_feedback_2=row[10],
                        choice_feedback_3=row[11],
                        choice_feedback_4=row[12],
                        marks=int(row[13])
                    )
                    db.session.add(question)
                elif question_type == 'st':
                    question = StQuestion(
                        question=row[1],
                        correct_ans=row[2],
                        feedback_correct=row[3],
                        feedback_wrong=row[4],
                        marks=int(row[5])
                    )
                    db.session.add(question)
            db.session.commit()
            flash('CSV file uploaded successfully!', category="success")
            return redirect(url_for('questions'))
        else:
            flash('Invalid file format! Only CSV files are allowed.')
            return redirect(request.url)
    return render_template('upload_csv.html')

# Testing export file part

@app.route('/export_questions/<tag>', methods=['GET'])
def export_questions(tag):
    # Get mc questions and st questions related to the selected tag
    mc_questions = McQuestion.query.filter(McQuestion.tags.any(Tag.tag == tag)).all()
    st_questions = StQuestion.query.filter(StQuestion.tags.any(Tag.tag == tag)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Question Type', 'Question', 'Multiple Choice', 'Feedback', 'Difficulty', 'Tags', 'Marks', 'Choice 1', 'Choice 1 Feedback', 'Choice 2', 'Choice 2 Feedback', 'Choice 3', 'Choice 3 Feedback', 'Choice 4', 'Choice 4 Feedback', 'Correct Answer', 'Correct Feedback', 'Incorrect Feedback'])
    
    for mc_question in mc_questions:
        row = ['Multiple Choice', mc_question.question, mc_question.multiple, mc_question.feedback, mc_question.difficulty.name if mc_question.difficulty else "", ",".join([tag.tag for tag in mc_question.tags]), mc_question.marks]
        for choice in mc_question.choices:
            row.append(choice.choice_text)
            row.append(choice.feedback)
        row.extend([mc_question.choice_1, mc_question.choice_feedback_1, mc_question.choice_2, mc_question.choice_feedback_2, mc_question.choice_3, mc_question.choice_feedback_3, mc_question.choice_4, mc_question.choice_feedback_4, "", ""])
        writer.writerow(row)

    for st_question in st_questions:
        row = ['Short Text', st_question.question, "", "", st_question.difficulty.name if st_question.difficulty else "", ",".join([tag.tag for tag in st_question.tags]), st_question.marks, "", "", "", "", "", "", "", st_question.correct_ans, st_question.feedback_correct, st_question.feedback_wrong]
        writer.writerow(row)

    # Return CSV file
    response = Response(output.getvalue(), content_type='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="questions.csv")
    return response



# Andy part end

@app.route("/courses", methods=['GET', 'POST'])
def courses():
  user = User.query.get(current_user.id)
  if user.student: courses = user.student.programme.courses if user.student.programme.courses else []
  else: courses = Course.query.all()
	# else: courses = user.teacher.courses if user.teacher.courses else []
  form = CourseForm()
  if form.validate_on_submit() and current_user.teacher:
    course = Course(number=form.number.data, name=form.name.data, description=form.description.data, programme_id=form.programme_id.data)
    db.session.add(course)
    db.session.flush()
    user.teacher.courses.append(course)
    db.session.commit()
    flash('Course created successfully!', category="success")
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
            # print(attempts)
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
    st_questions = StQuestion.query.order_by(StQuestion.id.asc()).paginate(page=1, per_page=8)
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
    mc_questions = McQuestion.query.order_by(McQuestion.id.asc()).paginate(page=1, per_page=8)
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

@app.route("/assessment/result/<int:attempt_id>", methods=['GET', 'POST'])
def assessment_result(attempt_id):
    user = User.query.get(current_user.id)
    attempt = StudentAttemptStatus.query.get(attempt_id)
    form = AttemptFeedbackForm()
    if form.validate_on_submit():
      attempt.feedback = form.feedback.data
      db.session.commit()
      return redirect(url_for("assessment_result", attempt_id=attempt_id))
    mc_feedbacks, mc_answers, st_answers = [], [], []
    for question in attempt.assessment.template.mc_questions:
        mc_feedbacks.append([question.choice_feedback_1, question.choice_feedback_2, question.choice_feedback_3, question.choice_feedback_4])
        mc_answer = db.session.query(McStudentAns).filter_by(attempt_id=attempt_id, question_id=question.id).first()
        mc_answers.append(mc_answer)
    for question in attempt.assessment.template.st_questions:
        st_answer = db.session.query(StStudentAns).filter_by(attempt_id=attempt_id, question_id=question.id).first()
        st_answers.append(st_answer)
    return render_template("assessment_result.html", user=user, attempt=attempt, assessment=attempt.assessment, mc_feedbacks=mc_feedbacks, mc_answers=mc_answers, st_answers=st_answers, mc_id_char=MC_ID_CHAR, form=form)

@app.route("/assessment/results/<int:assessment_id>", methods=['GET'])
def assessment_results(assessment_id):
    user = User.query.get(current_user.id)
    if not user.teacher:
        return redirect(url_for("courses"))
    assessment = Assessment.query.get(assessment_id)
    programme = assessment.course.programme
    student_attempt_records, student_attempt_times, student_not_attempt_records = [], [], []
    attempt_students_num = 0
    for student in programme.students:
        attempts = StudentAttemptStatus.query.filter_by(student_id=student.id, assessment=assessment)
        attempt = attempts.order_by(StudentAttemptStatus.id.desc()).first()
        if attempt:
          if assessment.is_formative:
              student_attempt_times.append(len(attempts.all()))
          student_attempt_records.append(attempt)
          attempt_students_num += 1
        else:
            not_attempt_record = StudentAttemptStatus(student=student, assessment=assessment)
            student_not_attempt_records.append(not_attempt_record)
    student_attempt_records.extend(student_not_attempt_records)
    return render_template("assessment_results.html", user=user, programme=programme, assessment=assessment, student_attempt_records=student_attempt_records, student_attempt_times=student_attempt_times, attempt_students_num=attempt_students_num)

@app.route("/assessment/result/confirm/<int:attempt_id>/<int:is_confirmed>", methods=['POST'])
def assessment_result_confirm(attempt_id, is_confirmed):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    attempt.result_is_confirmed = is_confirmed
    db.session.commit()
    return redirect(url_for("assessment_results", assessment_id=attempt.assessment.id))

@app.route("/assessment/results/confirm/<int:assessment_id>", methods=['POST'])
def assessment_results_confirm(assessment_id):
    attempts = StudentAttemptStatus.query.join(StudentAttemptStatus.assessment).filter(Assessment.id == assessment_id).all()
    for attempt in attempts:
        attempt.result_is_confirmed = True
        db.session.commit()
    return redirect(url_for("assessment_results", assessment_id=assessment_id))

@app.route("/attempt/feedback/<int:attempt_id>", methods=["POST"])
def attempt_feedback(attempt_id):
    attempt = StudentAttemptStatus.query.get(attempt_id)
    attempt

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

@app.route("/allcourses", methods=['GET'])
def allcourses():
    return render_template('allcourses.html')

@app.route("/formative", methods=['GET'])
def formative():
    return render_template('formative.html')

@app.route("/summative", methods=['GET'])
def summative():
    return render_template('summative.html')

@app.route("/CMT119", methods=['GET'])
def CMT119():
    return render_template('CMT119-table.html')

@app.route("/CMT119charts", methods=['GET'])
def CMT119charts():
    return render_template('CMT119-charts.html')

@app.route("/CMT120", methods=['GET'])
def CMT120():
    return render_template('CMT120-table.html')

@app.route("/CMT120charts", methods=['GET'])
def CMT120charts():
    return render_template('CMT120-charts.html')

@app.route("/CMT219", methods=['GET'])
def CMT219():
    return render_template('CMT219-table.html')

@app.route("/CMT219charts", methods=['GET'])
def CMT219charts():
    return render_template('CMT219-charts.html')

@app.route("/CMT220", methods=['GET'])
def CMT220():
    return render_template('CMT220-table.html')

@app.route("/CMT220charts", methods=['GET'])
def CMT220charts():
    return render_template('CMT220-charts.html')

@app.route("/CMT221", methods=['GET'])
def CMT221():
    return render_template('CMT221-table.html')

@app.route("/CMT221charts", methods=['GET'])
def CMT221charts():
    return render_template('CMT221-charts.html')

@app.route("/CMT313", methods=['GET'])
def CMT313():
    return render_template('CMT313-table.html')

@app.route("/CMT313charts", methods=['GET'])
def CMT313charts():
    return render_template('CMT313-charts.html')