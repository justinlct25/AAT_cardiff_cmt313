from aat import db

user_teacher_association_table = db.Table('user_teacher',
                                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                          db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                          db.PrimaryKeyConstraint('user_id', 'teacher_id')
                                          )

user_student_association_table = db.Table('user_student',
                                          db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                          db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                                          db.PrimaryKeyConstraint('user_id', 'student_id')
                                          )

teacher_courses_association_table = db.Table('teacher_courses',
                                            db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                            db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                                            db.PrimaryKeyConstraint('teacher_id', 'course_id')
                                            )

teacher_templates_association_table = db.Table('teacher_templates',
                                            db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.PrimaryKeyConstraint('teacher_id', 'template_id')
                                            )

teacher_st_questions_association_table = db.Table('teacher_st_questions',
                                            db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                            db.Column('st_question_id', db.Integer, db.ForeignKey('st_question.id')),
                                            db.PrimaryKeyConstraint('teacher_id', 'st_question_id')
                                            )

teacher_mc_questions_association_table = db.Table('teacher_mc_questions',
                                            db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                            db.Column('mc_question_id', db.Integer, db.ForeignKey('mc_question.id')),
                                            db.PrimaryKeyConstraint('teacher_id', 'mc_question_id')
                                            )

student_courses_association_table = db.Table('student_courses',
                                            db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                                            db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                                            db.PrimaryKeyConstraint('student_id', 'course_id')
                                            )

assessment_template_association_table = db.Table('assessment_assessment_template',
                                            db.Column('assessment_id', db.Integer, db.ForeignKey('assessment.id')),
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.PrimaryKeyConstraint('assessment_id', 'template_id')
                                            )

template_difficulty_association_table = db.Table('template_difficulty',
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.Column('difficulty_id', db.Integer, db.ForeignKey('difficulty.id')),
                                            db.PrimaryKeyConstraint('template_id', 'difficulty_id')
                                            )

template_tags_association_table = db.Table('template_tags',
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                                            db.PrimaryKeyConstraint('template_id', 'tag_id')
                                            )

template_mcquestions_association_table = db.Table('template_mcquestions',
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.Column('mcquestion_id', db.Integer, db.ForeignKey('mc_question.id')),
                                            db.PrimaryKeyConstraint('template_id', 'mcquestion_id')
                                            )

template_fbquestions_association_table = db.Table('template_fbquestions',
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.Column('fbquestion_id', db.Integer, db.ForeignKey('fb_question.id')),
                                            db.PrimaryKeyConstraint('template_id', 'fbquestion_id')
                                            )

template_stquestions_association_table = db.Table('template_stquestions',
                                            db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                            db.Column('stquestion_id', db.Integer, db.ForeignKey('st_question.id')),
                                            db.PrimaryKeyConstraint('template_id', 'stquestion_id')
                                            )

template_courses_association_table = db.Table('template_courses',
                                                db.Column('template_id', db.Integer, db.ForeignKey('assessment_template.id')),
                                                db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                                                db.PrimaryKeyConstraint('template_id', 'course_id')
                                                )

mcquestion_difficulty_association_table = db.Table('mcquestion_difficulty',
                                            db.Column('mcquestion_id', db.Integer, db.ForeignKey('mc_question.id')),
                                            db.Column('difficulty_id', db.Integer, db.ForeignKey('difficulty.id')),
                                            db.PrimaryKeyConstraint('mcquestion_id', 'difficulty_id')
                                            )

mcquestion_tags_association_table = db.Table('mcquestion_tags',
                                            db.Column('mcquestion_id', db.Integer, db.ForeignKey('mc_question.id')),
                                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                                            db.PrimaryKeyConstraint('mcquestion_id', 'tag_id')
                                            )

fbquestion_difficulty_association_table = db.Table('fbquestion_difficulty',
                                            db.Column('fbquestion_id', db.Integer, db.ForeignKey('fb_question.id')),
                                            db.Column('difficulty_id', db.Integer, db.ForeignKey('difficulty.id')),
                                            db.PrimaryKeyConstraint('fbquestion_id', 'difficulty_id')
                                            )

fbquestion_tags_association_table = db.Table('fbquestion_tags',
                                            db.Column('fbquestion_id', db.Integer, db.ForeignKey('fb_question.id')),
                                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                                            db.PrimaryKeyConstraint('fbquestion_id', 'tag_id')
                                            )

stquestion_difficulty_association_table = db.Table('stquestion_difficulty',
                                            db.Column('stquestion_id', db.Integer, db.ForeignKey('st_question.id')),
                                            db.Column('difficulty_id', db.Integer, db.ForeignKey('difficulty.id')),
                                            db.PrimaryKeyConstraint('stquestion_id', 'difficulty_id')
                                            )

stquestion_tags_association_table = db.Table('stquestion_tags',
                                            db.Column('stquestion_id', db.Integer, db.ForeignKey('st_question.id')),
                                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                                            db.PrimaryKeyConstraint('stquestion_id', 'tag_id')
                                            )

assessment_status_association_table = db.Table('assessment_status',
                                            db.Column('assessment_id', db.Integer, db.ForeignKey('assessment.id')),
                                            db.Column('status_id', db.Integer, db.ForeignKey('student_attempt_status.id')),
                                            db.PrimaryKeyConstraint('assessment_id', 'status_id')
                                            )

mcans_choices_association_table = db.Table('mcans_choices',
                                            db.Column('mcans_id', db.Integer, db.ForeignKey('mc_student_ans.id')),
                                            db.Column('choice_id', db.Integer, db.ForeignKey('choice.id')),
                                            db.PrimaryKeyConstraint('mcans_id', 'choice_id')
                                            )