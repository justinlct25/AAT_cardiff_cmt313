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

teacher_modules_association_table = db.Table('teacher_modules',
                                            db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')),
                                            db.Column('module_id', db.Integer, db.ForeignKey('module.id')),
                                            db.PrimaryKeyConstraint('teacher_id', 'module_id')
                                            )

student_modules_association_table = db.Table('student_modules',
                                            db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                                            db.Column('module_id', db.Integer, db.ForeignKey('module.id')),
                                            db.PrimaryKeyConstraint('student_id', 'module_id')
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

fbquestion_difficulty_association_table = db.Table('fbcquestion_difficulty',
                                            db.Column('fbquestion_id', db.Integer, db.ForeignKey('fb_question.id')),
                                            db.Column('difficulty_id', db.Integer, db.ForeignKey('difficulty.id')),
                                            db.PrimaryKeyConstraint('fbquestion_id', 'difficulty_id')
                                            )

fbquestion_tags_association_table = db.Table('fbquestion_tags',
                                            db.Column('fbquestion_id', db.Integer, db.ForeignKey('fb_question.id')),
                                            db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                                            db.PrimaryKeyConstraint('fbquestion_id', 'tag_id')
                                            )

assessment_status_association_table = db.Table('assessment_status',
                                            db.Column('assessment_id', db.Integer, db.ForeignKey('assessment.id')),
                                            db.Column('status_id', db.Integer, db.ForeignKey('student_assessment_status.id')),
                                            db.PrimaryKeyConstraint('assessment_id', 'status_id')
                                            )

mcans_choices_association_table = db.Table('mcans_choices',
                                            db.Column('mcans_id', db.Integer, db.ForeignKey('mc_student_ans.id')),
                                            db.Column('choice_id', db.Integer, db.ForeignKey('choice.id')),
                                            db.PrimaryKeyConstraint('mcans_id', 'choice_id')
                                            )