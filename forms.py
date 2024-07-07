from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, validators
from wtforms.validators import DataRequired,NumberRange
 


class DeliveryForm(FlaskForm):
    door_no = StringField('Door No')
    street_name = StringField('Street Name')
    area = StringField('Area')
    landmark = StringField('Landmark')
    pincode = StringField('Pincode')
    district = StringField('District')
    mobile_number = StringField('Mobile Number')
    submit = SubmitField('Save') 

 