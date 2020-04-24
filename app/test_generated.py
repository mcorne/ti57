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


# Scientific notation (EE)
ee = False
# Memories (STO)
mem = [0 for i in range(8)]
# Registers of intermediate values rounded and displayed after each pause (2nd Pause)
regx = []
# Internal memory stack used for computing nested operations
stack = []
# Number of digit after the decimal point (2nd Fix)
rounding = None
# Angle unit (DEG, RAD, GRAD)
unit = "Deg"
# Display
x = 0


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


def roundn(number):
    global rounding
    if rounding is not None:
        number = round(number, rounding)
    return number


def state():
    global ee, mem, regx, rounding, stack, unit, x
    state = {
        "ee": ee,
        "mem": mem,
        "regx": regx,
        "rounding": rounding,
        "stack": stack,
        "unit": unit,
        "x": x,
        "xrounded": roundn(x),
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
    # Volume of a cylinder
    
    # Calculate the volume: π x radius² x height
    # We'll have for example a volume of  of 314.16 for a diameterof 10 and a height of 4.
    
    # Source: Training with your EC-4000 Programmable Calculator by Texas Instruments, 1977, page 3-18
    # https://1drv.ms/b/s!ArcO_mFRe1Z9yia_fdpsnBaOeEXc?e=uCJpdM
    
    # Input
    # Enter diameter
    x = 10             # 10
    mem[1] = x         # STO 1     (32 0)
    # Enter height
    x = 4              # 4
    mem[2] = x         # STO 2     (32 0)
    
    # Main program
    rounding = 2       # 2nd Fix 2 (48)
    # Radius =  diameter / 2
    x = mem[1]         # RCL 1     (33 0)
    stack.append(x)    # /         (45)
    x = 2              # 2
    y = stack.pop()    # =         (85)
    x = y / x
    # Area = π x radius²
    x *= x             # x2        (23)
    stack.append(x)    # X         (55)
    x = pi             # 2nd pi    (30)
    # Volume = area X height
    y = stack.pop()    # X         (55)
    x = y * x
    stack.append(x)
    x = mem[2]         # RCL 2     (33 0)
    y = stack.pop()    # =         (85)
    x = y * x
    raise Stop()       # R/S       (81)
