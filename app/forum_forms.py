from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Subject, Course, Chapter, Lesson



class ReplyForm(FlaskForm):
    content = TextAreaField(_l('Reply Something'), validators=[DataRequired(),Length(min=0, max=10000)])
    parent_id = IntegerField(_l('Reply to'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class EditReplyForm(FlaskForm):
    reply_active = IntegerField(_l('Reply Active'), validators=[DataRequired()])
    content = TextAreaField(_l('Reply Something'), validators=[DataRequired(),Length(min=0, max=10000)])
    submit = SubmitField(_l('O'))


class TopicForm(FlaskForm):
    title = TextAreaField(_l('Write Title'), validators=[DataRequired(),Length(min=0, max=50)])
    content = TextAreaField(_l('Write Something'), validators=[DataRequired(),Length(min=0, max=10000)])
    tagname = TextAreaField(_l('Write Tags'), validators=[Length(min=0, max=50)])
    submit = SubmitField(_l('Submit'))
