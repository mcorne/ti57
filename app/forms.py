from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    split_instruction_from_py_lines = BooleanField(
        "Split/Join Instructions from/with Python lines of code"
    )
    submit = SubmitField("Run")
    ti_instructions = TextAreaField("Instructions")
