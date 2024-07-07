# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Image')
    specifications = TextAreaField('Specifications')
    features = TextAreaField('Features')
    warranty = TextAreaField('Warranty')
    submit = SubmitField('Upload Product')
