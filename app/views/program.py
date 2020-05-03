from flask import Blueprint, flash, make_response, render_template, request
from flask_babel import _

from app.forms import ProgramForm
from app.models.calculator import Stop, get_calculator_state
from app.models.translator import Translator

bp = Blueprint("program", __name__)


@bp.route("/", methods=("GET", "POST"))
def index():
    calculator_state = {}
    py_code_part = ""
    ti_instructions = ""
    form = ProgramForm()
    try:
        if form.validate_on_submit():
            ti_instructions = form.ti_instructions.data
            translator = Translator()
            py_code, py_code_part = translator.generate_py_code(
                ti_instructions, form.instruction_not_with_python.data
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
                if request.cookies.get("instruction_not_with_python", "0") == "1":
                    form.instruction_not_with_python.data = True
                else:
                    form.instruction_not_with_python.data = False
    except FileNotFoundError:
        flash("Invalid example", "error")
    except Stop:
        calculator_state = get_calculator_state()
    except Exception as e:
        flash(e, "error")

    if "stack" in calculator_state and calculator_state["stack"]:
        flash("Syntax Error: unbalanced or misused parentheses", "error")

    template = render_template(
        "program/index.html",
        calculator_state=calculator_state,
        form=form,
        py_code_part=py_code_part,
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
