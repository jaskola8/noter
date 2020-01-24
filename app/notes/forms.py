from flask_wtf.form import FlaskForm
from wtforms import TextAreaField, StringField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired


class NewNoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    is_public = BooleanField("Public note")
    give_access = SelectMultipleField('Select users to give access to', coerce=int)


class EditNoteForm(NewNoteForm):
    revoke_access = SelectMultipleField('Select users to revoke access', coerce=int)
