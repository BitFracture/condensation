"""Representation of forms for flask wtf"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class CreateThreadForm(FlaskForm):
    """Class representing the create thread form"""
    heading = StringField("Heading", validators=[DataRequired()])
    body = StringField("Body", validators=[DataRequired()])
    submit = SubmitField("Create Thread")
