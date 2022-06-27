from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, FileField, SelectField, DateTimeField
from wtforms.validators import InputRequired, Email, DataRequired
from flask_wtf.file import FileRequired, FileAllowed

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    profile_photo = FileField('Upload Photo', validators=[FileRequired(), FileAllowed(['jpg','png', 'jpeg'],'Images only!')])
    role = SelectField(u'Role' ,choices=[('Admin','Admin'),('Regular','Regular')])

class EventForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    start_date = DateTimeField('Start Date and Time', validators=[InputRequired()])
    end_date = DateTimeField('End Date and Time', validators=[InputRequired()])
    desc = TextAreaField('Description', validators=[InputRequired(),DataRequired()])
    venue = StringField('Venue', validators=[InputRequired()])
    flyer = FileField('Upload Photo', validators=[FileRequired(), FileAllowed(['jpg','png', 'jpeg'],'Images only!')])
    website_url = StringField('Website URL', validators=[InputRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[InputRequired()])
