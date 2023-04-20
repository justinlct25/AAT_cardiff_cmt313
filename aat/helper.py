def update_template_total_marks(template):
    total_marks = 0
    for question in template.mc_questions:
        total_marks += question.marks
    for question in template.st_questions:
        total_marks += question.marks
    template.total_marks = total_marks