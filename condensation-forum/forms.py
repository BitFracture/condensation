"""Representation of forms for flask wtf"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators

class CreateThreadForm(FlaskForm):
    """Class representing the create thread form"""
    heading = StringField("Heading", [validators.required(), validators.length(max=120)])
    body = TextAreaField("Body", [validators.required(), validators.length(max=200000)])
    submit = SubmitField("Post")

class CreateCommentForm(FlaskForm):
    """Class representing the create comment form"""
    body = TextAreaField("Body", [validators.required(), validators.length(max=200000)])
    submit = SubmitField("Post")
