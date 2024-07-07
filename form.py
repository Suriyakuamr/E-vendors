from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Length

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Sign Up')

    def validate_email(form, field):
        if not field.data.endswith('@gmail.com'):
            raise ValidationError('Email must be a Gmail address.')

    def validate_phone_number(form, field):
        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError('Phone number must be exactly 10 digits long.')
 
 
 
 
  