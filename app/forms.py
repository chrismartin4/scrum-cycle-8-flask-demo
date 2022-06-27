from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, FileField, SelectField
from wtforms.validators import InputRequired, Email, FileRequired, FileAllowed

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    profile_photo=FileField('Upload Photo',validators=[FileRequired(),FileAllowed(['jpg','png', 'jpeg'],'Images only!')])
    role=SelectField(u'Role' ,choices=[('Admin','Admin'),('Regular','Regular')])

class EventForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    