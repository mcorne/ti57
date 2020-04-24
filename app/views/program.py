from flask import Blueprint, render_template
from flask_babel import _

from app.models.generator import Generator
from app.models.calculator import state, Stop

bp = Blueprint("program", __name__)


@bp.route("/")
def index():
    with open("app/examples/on-sale.txt", "r") as file:
        ti_instructions = file.read()

    try:
        g = Generator()
        code = g.generate_py_code(ti_instructions)
        with open("app/test_generated.py", "w") as file:
            file.write(code)
        print(code)
        exec(code, globals())
        main()
        print(state())
    except Stop as e:
        print(state())
    except Exception as e:
        print(e)

    return render_template("program/index.html")
