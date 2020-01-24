from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],)
    password = PasswordField('Password', validators=[DataRequired()],)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(10)])
    rep_password = PasswordField('Repeat password', validators=[
        DataRequired(), EqualTo('password', 'Passwords do not match'), Length(10)
    ])


class PassChangeForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(10)])
    rep_new_password = PasswordField('Repeat New Password', validators=[
        DataRequired(), EqualTo('new_password', 'Passwords do not match'), Length(10)
    ])
