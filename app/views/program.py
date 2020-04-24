from flask import Blueprint, render_template
from flask_babel import _

from app.models.generator import Generator

bp = Blueprint("program", __name__)


@bp.route("/")
def index():
    ti_instructions = """
            500 STO 1 # comment 1
            0.015 STO 2

            3 STO 3 # comment 2
            1
            # comment 3
            INV 2nd Prod 3
            RCL 1 *
            ( RCL 2 /
            ( 1 - ( 1 + RCL 2 )
            Y^X RCL 3 +/- ) ) =
            45 2nd sin =
            """

    # ti_instructions = """
    #         10.25 EE 2 * 3 =
    #         """

    # ti_instructions = """
    #         1 y^x 2 y^x 3 INV y^x 4 y^x 5 =
    #         """

    # ti_instructions = """
    #         1 * 3 + 4 * 5 y^x 2 - 7 / 8 =
    #         """

    # ti_instructions = """
    #         2 y^x 3 / 2 =
    #         """

    # 27
    # ti_instructions = "(1+2) * (4+5) ="

    # [x] => 4.916523412787E-10
    # ti_instructions = "1 * 2 / 3 y^x 4 y^x 5 * 6 / 7 ="

    # ti_instructions = """
    #         90 2nd sin =
    #         +/- INV 2nd cos =
    #         """

    # ti_instructions = """
    #         5 STO 7
    #         2 2nd Exc 7
    #         RCL 7
    #         """

    # ti_instructions = """
    #         5 STO 7
    #         2 x<>t
    #         RCL 7
    #         """

    # ti_instructions = """
    #         5 STO 7
    #         2 + 3 * ( 5 + 6
    #         CLR
    #         1+2=
    #         RCL 7
    #         """

    # ti_instructions = "5 STO 1 INV 2nd Ct RCL 1"

    # ti_instructions = """
    #         45.153030 +/-
    #         2nd D.MS
    #         """

    # ti_instructions = """
    #         45.153030
    #         2nd D.MS
    #         INV 2nd D.MS
    #         """

    # ti_instructions = "3 2nd Fix 10 x<>t 120 2nd P->R x<>t"

    # ti_instructions = """
    #         3 2nd Fix
    #         1 x<>t 2 +/- INV 2nd P->R x<>t
    #         """

    # ti_instructions = "2nd pi 2nd Int "
    # ti_instructions = "2nd pi INV 2nd Int"

    # ti_instructions = """
    #         2.5 +/- STO 0
    #         INV 2nd Dsz
    #         4
    #         5
    #         """

    # ti_instructions = """
    #         1 STO 7
    #         2
    #         2nd x=t
    #         3
    #         4
    #         """

    # ti_instructions = """
    #         2 x<>t 10 2nd S+
    #         3 x<>t 20 2nd S+
    #         5 x<>t 30 2nd S+
    #         6 x<>t 40 2nd S+
    #         10 x<>t 2 2nd S+
    #         10 x<>t 2 INV 2nd S+
    #         10 x<>t 2 2nd S+
    #         INV 2nd x
    #         2nd x
    #         INV 2nd s2
    #         2nd s2
    #         """

    # ti_instructions = """
    #         # comment 1
    #         # comment 2
    #         5 STO 4
    #         # comment 3
    #         SBR 1
    #         # func 1
    #         # func 11
    #         # func 111
    #         2nd Lbl 0
    #         # func 1111
    #         3 STO 4
    #         2.5 +/- STO 0
    #         # comment 4
    #         2nd Dsz
    #         # comment 5
    #         4
    #         5
    #         INV SBR
    #         2nd Lbl 1
    #         2 STO 4
    #         # call 0
    #         # call 00
    #         SBR 0
    #         INV SBR
    #         """

    try:
        g = Generator()
        code = g.generate_py_code(ti_instructions)
        with open("app/test_generated.py", "w") as file:
            file.write(code)
        print(code)
        exec(code, globals())
        main()
    except Stop as e:
        pass

    print(state())
    return render_template("program/index.html")
