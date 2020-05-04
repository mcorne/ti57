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


def grd2rad(number):
    return (number / 200) * pi


def get_calculator_state():
    global ee, error, mem, regx, rounding, stack, unit, x
    return {
        "ee": ee,
        "mem": mem,
        "regx": regx,
        "rounding": rounding,
        "stack": stack,
        "unit": unit,
        "x": x,
        "xrounded": roundn(x),
    }


def init_calculator():
    global ee, error, mem, regx, rounding, stack, unit, x
    # Scientific notation (EE)
    ee = False
    # Syntax error etc.
    error = None
    # Memories (STO)
    mem = [0 for i in range(8)]
    # History of values displayed before a pause (2nd pause)
    regx = []
    # Internal memory stack used for computing nested operations
    stack = []
    # Number of digit after the decimal point (2nd Fix)
    rounding = None
    # Angle unit (2nd Deg, 2nd Rad, 2nd Grad)
    unit = "Deg"
    # Display
    x = 0


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


def roundn(number):
    global rounding
    if rounding is not None:
        number = round(number, rounding)
    return number


def unit2rad(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = radians(number)
    elif unit == "Grd":
        number = grd2rad(number)
    return number


# Program execution

try:
    init_calculator()
    main()
except UserWarning:  # R/S
    pass
except Exception as e:
    error = str(e)

# print(get_calculator_state())
