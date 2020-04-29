from flask import Blueprint, flash, make_response, render_template, request
from flask_babel import _

from app.forms import ProgramForm
from app.models.calculator import Stop, get_calculator_state
from app.models.translator import Translator

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
                ti_instructions, form.split_instructions_from_py_lines.data
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
                form.split_instructions_from_py_lines.data = request.cookies.get(
                    "split_instructions_from_py_lines", False
                )
    except FileNotFoundError:
        flash("Invalid example", "error")
    except Stop:
        calculator_state = get_calculator_state()
    except Exception as e:
        flash(e, "error")

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
        "split_instructions_from_py_lines",
        str(form.split_instructions_from_py_lines.data),
        max_age,
    )
    return response
