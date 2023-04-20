from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Subject, Course, Chapter, Lesson


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class AddSubjectForm(FlaskForm):
    name = TextAreaField(_l('Subject Name'),
                         validators=[Length(min=0, max=70), DataRequired()])
    desc = TextAreaField(_l('Subject Description'),
                         validators=[Length(max=600), DataRequired()])
    type = SelectField(_l('Subject Type'), choices=[('Language', 'Language'),
                                                    ('Other','Other')],
                                                     validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class AddCourseForm(FlaskForm):
    name = TextAreaField(_l('Course Name'),
                         validators=[Length(min=0, max=70), DataRequired()])
    desc = TextAreaField(_l('Course Description'),
                         validators=[Length(max=600), DataRequired()])
    path = SelectField(_l('Course Path'), choices=[('Career', 'Career'),
                                                   ('Skill','Skill'),
                                                   ('None','None')],
                                                     validators=[DataRequired()])
    related_subj = SelectField('Subject', choices=[])
    submit = SubmitField(_l('Submit'))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_subj.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

class AddChapterForm(FlaskForm):
    title = TextAreaField(_l('Chapter Title'),
                         validators=[Length(min=0, max=70), DataRequired()])
    course_id = SelectField('Course', choices=[], validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.course_id.choices = [(course.id, course.coursename) for course in Course.query.all()]


class AddLessonForm(FlaskForm):
    name = TextAreaField(_l('Lesson name'),
                         validators=[Length(min=0, max=70), DataRequired()])
    related_subj = SelectField('Subject', choices=[], validators=[DataRequired()])
    chapter_id = SelectField('Chapter', choices=[], validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_subj.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
        self.chapter_id.choices = [(chapter.id, chapter.title) for chapter in Chapter.query.all()]

