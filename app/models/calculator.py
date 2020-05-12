import re
from math import *
from goto import with_goto  # pip install goto-statement


@with_goto
def main():
    global ee, mem, rounding, stack, unit, x
    label.label_rst


# Internal functions


def degrees2dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds."""
    degrees = float(degrees)
    is_positive = degrees >= 0
    if not is_positive:
        degrees = -degrees

    minutes, seconds = divmod(degrees * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    # Internal mantissa has 11 digits on TI-57
    seconds = f"{seconds:016.13f}".replace(".", "")

    dms = f"{int(degrees)}.{int(minutes):02}{seconds}".rstrip("0")
    if not is_positive:
        dms = "-" + dms
    return dms


def dms2degrees(dms):
    """Convert degrees, minutes, seconds to decimal degrees."""
    match = re.fullmatch(
        r"(?P<sign>[+-])?(?P<degrees>[0-9]+)\.?(?P<minutes>[0-9]{1,2})?(?P<seconds>[0-9]{1,2})?(?P<remainder>[0-9]*)",
        str(dms),
    )
    if match is None:
        raise Exception(f"Calculator error: invalid DMS angle {dms}")

    angle = match.groupdict()
    degrees = float(angle["degrees"])

    if angle["minutes"]:
        if len(angle["minutes"]) == 1:
            angle["minutes"] += "0"
        degrees += float(angle["minutes"]) / 60

    if angle["seconds"]:
        if len(angle["seconds"]) == 1:
            angle["seconds"] += "0"
        degrees += float(angle["seconds"]) / 3600

    if angle["remainder"]:
        degrees += float("0." + angle["remainder"]) / 3600

    if angle["sign"] == "-":
        degrees = -degrees
    return degrees


def fix(number):
    """Round a number and/or convert it to the scientific notation."""
    global ee, rounding
    if ee:
        # The scientific notation is on
        if rounding is None:
            # Default to the calculator 7 digit precision
            number = f"{number:.7E}"
            # Remove trailing 0's
            number = re.sub("0+E", "E", number)
        else:
            # Round as exponent with the given precision
            number = f"{number:.{rounding}E}"
    elif rounding is not None:
        # Rounding is on
        number = f"{number:.{rounding}f}"
    else:
        # No rounding
        number = str(number)
    return number


def grd2rad(gradian):
    """Convert gradian to radian."""
    return (gradian / 200) * pi


def get_calculator_state():
    """Return the calculator sate."""
    global ee, error, mem, regx, rounding, stack, unit, x
    return {
        "ee": ee,
        "error": error,
        "fixed_x": fix(x),
        "mem": mem,
        "regx": regx,
        "rounding": rounding,
        "stack": stack,
        "unit": unit,
        "x": x,
    }


def init_calculator_state(state={}):
    """Initialize the calculator state.

        Must be called before running the program, see run().
        ee       -- Scientific notation (EE)
        error    -- Syntax error etc.
        mem      -- Memories (STO)
        regx     -- History of values displayed before a pause (2nd pause)
        rounding -- Number of digit after the decimal point (2nd Fix)
        stack    -- Internal memory stack used for computing nested operations
        unit     -- Angle unit (2nd Deg, 2nd Rad, 2nd Grad)
        x        -- Display register or X register
    """
    global ee, error, mem, regx, rounding, stack, unit, x
    ee = state["ee"] if "ee" in state else False
    error = state["error"] if "error" in state else None
    mem = state["mem"] if "mem" in state else [0 for i in range(8)]
    regx = state["regx"] if "regx" in state else []
    rounding = state["rounding"] if "rounding" in state else None
    stack = state["stack"] if "stack" in state else []
    unit = state["unit"] if "unit" in state else "Deg"
    x = state["x"] if "x" in state else 0


def rad2grd(radian):
    """Convert radian to gradian."""
    return (radian / pi) * 200


def rad2unit(number):
    """Convert radian to degree or gradian."""
    global unit
    number = float(number)
    if unit == "Deg":
        number = degrees(number)
    elif unit == "Grd":
        number = rad2grd(number)
    return number


def run_program():
    """Run the program (the entry point).
       The calculator must be initialized beforehand, see init_calculator_state().
    """
    global error, x
    try:
        main()
    except ZeroDivisionError:
        x = 9.9999999
    except UserWarning:  # R/S key
        pass
    except Exception as e:
        error = str(e)


def unit2rad(number):
    """Convert degree or gradian to radian."""
    global unit
    number = float(number)
    if unit == "Deg":
        number = radians(number)
    elif unit == "Grd":
        number = grd2rad(number)
    return number


# Program execution, uncomment to run the file on its own.
# init_calculator_state()
# run_program()
# calculator_state = get_calculator_state()
# print(calculator_state)
