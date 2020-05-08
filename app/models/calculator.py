import re
from math import *
from goto import with_goto


@with_goto
def main():
    global ee, mem, rounding, stack, unit, x
    label.label_rst


# Internal functions


def degrees2dms(degrees):
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
    global ee, rounding
    if ee:
        # The scientific notation is on
        if rounding is None:
            # Default to the calculator 7 digit precision
            number = f"{number:.7E}"
            # Remove trailing 0's
            number = re.sub("0+E", "E", number)
        else:
            number = f"{number:.{rounding}E}"
    elif rounding is not None:
        number = f"{number:.{rounding}f}"
    return number


def grd2rad(number):
    return (number / 200) * pi


def get_calculator_state():
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
    """Initialize the calculator state

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


def rad2grd(number):
    return (number / pi) * 200


def rad2unit(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = degrees(number)
    elif unit == "Grd":
        number = rad2grd(number)
    return number


def run_program():
    global error
    try:
        main()
    except UserWarning:  # R/S
        pass
    except Exception as e:
        error = str(e)


def unit2rad(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = radians(number)
    elif unit == "Grd":
        number = grd2rad(number)
    return number


# Example of program execution
# init_calculator_state()
# run_program()
# calculator_state = get_calculator_state()
# print(calculator_state)
