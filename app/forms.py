from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    submit = SubmitField("Run")
    ti_instructions = TextAreaField("Instructions")
