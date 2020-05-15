import json
from random import random

from flask import (
    Blueprint,
    flash,
    make_response,
    render_template,
    request,
    send_from_directory,
)
from flask_babel import _

from app.forms import ProgramForm
from app.models.calculator import (
    get_calculator_state,
    init_calculator_state,
    run_program,
)
from app.models.translator import Translator

bp = Blueprint("program", __name__)


def fix_ti_instructions(ti_instructions):
    # Replace the seed number used in some programs to initialize a random generator
    seed = round(random(), 6)
    ti_instructions = ti_instructions.replace("0.123456 STO", str(seed) + " STO")
    return ti_instructions


@bp.route("/", methods=("GET", "POST"))
def index():
    calculator_state = {}
    py_code = ""
    ti_instructions = ""
    translator = Translator()
    form = ProgramForm()
    try:
        if form.validate_on_submit():
            ti_instructions = form.ti_instructions.data
            py_code = translator.generate_py_code(
                ti_instructions, form.instruction_not_with_python.data
            )
            exec(py_code, globals())
            init_calculator_state(json.loads(form.calculator_state.data))
            run_program()
            calculator_state = get_calculator_state()
        else:
            program = request.args.get("program", "introduction")
            with open(f"app/programs/{program}.txt", "r") as file:
                ti_instructions = file.read()
                ti_instructions = fix_ti_instructions(ti_instructions)
                form.ti_instructions.data = ti_instructions
                if request.cookies.get("instruction_not_with_python", "0") == "1":
                    form.instruction_not_with_python.data = True
                else:
                    form.instruction_not_with_python.data = False
                py_code = translator.generate_py_code(
                    ti_instructions, form.instruction_not_with_python.data
                )
                init_calculator_state()
                calculator_state = get_calculator_state()
    except FileNotFoundError:
        flash("Invalid program name")
    except Exception as e:
        flash(e)

    form.calculator_state.data = json.dumps(calculator_state)
    if "error" in calculator_state and calculator_state["error"]:
        flash(calculator_state["error"])

    # Save the Python code to a file, uncomment for debugging purposes.
    with open("app/.~test_generated.py", "w") as file:
        file.write(py_code)

    template = render_template(
        "program/index.html",
        calculator_state=calculator_state,
        form=form,
        py_code=py_code,
        ti_instructions=ti_instructions,
    )

    response = make_response(template)
    max_age = 3600 * 24 * 30  # 30 days
    response.set_cookie(
        "instruction_not_with_python",
        str(int(form.instruction_not_with_python.data)),
        max_age,
    )
    return response


@bp.route("/docs/<filename>")
def send_pdf(filename):
    return send_from_directory("static/docs", filename)
