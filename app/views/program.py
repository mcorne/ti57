from flask import Blueprint, flash, render_template, request
from flask_babel import _

from app.models.translator import Translator
from app.models.calculator import get_calculator_state, Stop
from app.forms import ProgramForm

bp = Blueprint("program", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    py_code_part = ""
    calculator_state = []
    form = ProgramForm()
    try:
        if form.validate_on_submit():
            ti_instructions = form.ti_instructions.data
            translator = Translator()
            py_code, py_code_part = translator.generate_py_code(
                ti_instructions, form.split_instruction_from_py_lines.data
            )
            with open("app/.~test_generated.py", "w") as file:  # TODO: remove !!!
                file.write(py_code)
                exec(py_code, globals())
                init_calculator()
                main()
                calculator_state = get_calculator_state()
        else:
            example = request.args.get("example", "introduction")
            with open(f"app/examples/{example}.txt", "r") as file:
                ti_instructions = file.read()
                form.ti_instructions.data = ti_instructions
    except FileNotFoundError:
        flash("Invalid example", "error")
    except Stop:
        calculator_state = get_calculator_state()
    except Exception as e:
        flash(e, "error")

    return render_template(
        "program/index.html",
        calculator_state=calculator_state,
        form=form,
        py_code_part=py_code_part,
        ti_instructions=ti_instructions,
    )
