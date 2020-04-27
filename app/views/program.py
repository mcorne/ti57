from flask import Blueprint, flash, render_template, request
from flask_babel import _

from app.models.generator import Generator
from app.models.calculator import state, Stop

bp = Blueprint("program", __name__)


@bp.route("/")
def index():
    example = request.args.get("example")
    if example:
        try:
            with open(f"app/examples/{example}.txt", "r") as file:
                ti_instructions = file.read()

            g = Generator()
            code = g.generate_py_code(ti_instructions)
            with open("app/test_generated.py", "w") as file:
                file.write(code)
            print(code)
            exec(code, globals())
            main()
            print(state())
        except FileNotFoundError:
            flash("Invalid example", "error")
        except Stop:
            pass
        except Exception as e:
            flash(e, "error")

    return render_template("program/index.html")
