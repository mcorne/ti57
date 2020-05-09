import json

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    calculator_state = HiddenField(default=json.dumps({}))
    instruction_not_with_python = BooleanField(
        "Show instructions above the corresponding line of Python (recommended on small screens)"
    )
    run = SubmitField("Run")  # different from submit not to clash with form.submit()
    ti_instructions = TextAreaField("Instructions")
