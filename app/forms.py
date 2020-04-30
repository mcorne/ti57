from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    instruction_not_with_python = BooleanField(
        "Show instructions as comments above the corresponding line of Python code (recommended for small screens)"
    )
    submit = SubmitField("Run")
    ti_instructions = TextAreaField("Instructions")
