from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    instruction_with_python = BooleanField(
        "Display the instructions on the same line as the Python code (recommended on large screens)"
    )
    submit = SubmitField("Run")
    ti_instructions = TextAreaField("Instructions")
