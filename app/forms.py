from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    split_instructions_from_py_lines = BooleanField(
        "Split Instructions from Python lines of code"
    )
    submit = SubmitField("Run")
    ti_instructions = TextAreaField("Instructions")
