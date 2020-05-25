import json

from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SubmitField, TextAreaField


class ProgramForm(FlaskForm):
    calculator_state = HiddenField(default=json.dumps({}))
    run = SubmitField("Run")  # Different from submit not to clash with form.submit()
    ti_instructions = TextAreaField("Instructions")
