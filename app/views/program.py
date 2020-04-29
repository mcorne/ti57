from flask import Blueprint, flash, render_template, request
from flask_babel import _

from app.models.generator import Generator
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
            exec_code = True
            ti_instructions = form.ti_instructions.data
        else:
            exec_code = False
            example = request.args.get("example", "introduction")
            with open(f"app/examples/{example}.txt", "r") as file:
                ti_instructions = file.read()
                form.ti_instructions.data = ti_instructions
        generator = Generator()
        py_code, py_code_part = generator.generate_py_code(ti_instructions)
        with open("app/test_generated.py", "w") as file:  # TODO: remove !!!
            file.write(py_code)
        if exec_code:
            exec(py_code, globals())
            init_calculator()
            main()
            calculator_state = get_calculator_state()
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
