import re
from math import (
    acos,
    asin,
    atan,
    atan2,
    cos,
    degrees,
    exp,
    floor,
    log,
    log10,
    pi,
    pow,
    radians,
    sin,
    sqrt,
    tan,
)

from goto import with_goto


class Stop(Exception):
    pass


ee = False  # Disable scientific notation
mem = [0 for i in range(8)]  # Reset memory
stack = []  # Reset internal registers
rounding = None  # Disable rounding of numbers
unit = "Deg"  # Set degree mode
x = 0  # Reset display


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
        raise Exception(f"Invalid DMS angle {dms}")

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


def state():
    global ee, mem, rounding, stack, unit, x
    rounded = x if rounding is None else round(x, rounding)
    state = {
        "ee": ee,
        "mem": mem,
        "stack": stack,
        "rounded": rounded,
        "rounding": rounding,
        "unit": unit,
        "x": x,
    }
    return state


def unit2rad(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = radians(number)
    elif unit == "Grd":
        number = grd2rad(number)
    return number


@with_goto
def main():
    global ee, mem, rounding, stack, unit, x
    label.label_rst
    # comment 1
    x = 500            # 500
    mem[1] = x         # STO 1     (32 0)
    x = 0.015          # 0.015
    mem[2] = x         # STO 2     (32 0)
    
    # comment 2
    x = 3              # 3
    mem[3] = x         # STO 3     (32 0)
    # comment 3
    x = 1              # 1
    mem[3] /= x        # INV 2nd Prod 3 (- 39 0)
    x = mem[1]         # RCL 1     (33 0)
    stack.append(x)    # *         (55)
                       # (         (43)
    x = mem[2]         # RCL 2     (33 0)
    stack.append(x)    # /         (45)
                       # (         (43)
    x = 1              # 1
    stack.append(x)    # -         (65)
                       # (         (43)
    x = 1              # 1
    stack.append(x)    # +         (75)
    x = mem[2]         # RCL 2     (33 0)
    y = stack.pop()    # )         (44)
    x = y + x
    stack.append(x)    # Y^X       (35)
    x = mem[3]         # RCL 3     (33 0)
    x = -x             # +/-       (84)
    y = stack.pop()    # )         (44)
    x = pow(y, x)
    y = stack.pop()
    x = y - x
    y = stack.pop()    # )         (44)
    x = y / x
    y = stack.pop()    # =         (85)
    x = y * x
    x = 45             # 45
    x = sin(unit2rad(x)) # 2nd sin   (28)
                       # =         (85)
