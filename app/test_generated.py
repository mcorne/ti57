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
    # Sign posts
    
    # Calculate the area of a square: side².
    # Calculate the volume of a cube: side³.
    # Calculate the area of a circle: π x radius².
    # Calculate the volume of a sphere: 4/3π x radius³.
    # For example, we'll have respectively 38.07, 234.89 for a side of 6.17, and 27.9, 110.85 and a radius of 2.98.
    # Note that each pause is simulated by storing each intermediate result in a register.
    
    # Source: Training with your EC-4000 Programmable Calculator by Texas Instruments, 1977, page 3-23
    # https://1drv.ms/b/s!ArcO_mFRe1Z9yia_fdpsnBaOeEXc?e=uCJpdM
    
    # Input
    # Enter the side
    x = 6.17           # 6.17
    mem[0] = x         # STO 0     (32 0)
    # Enter the radius
    x = 2.98           # 2.98
    mem[1] = x         # STO 1     (32 0)
    
    # Main program
    rounding = 2       # 2nd Fix 2 (48)
    x = mem[0]         # RCL 0     (33 0)
    # Call subroutine 1 to calculate the area of a square
    sbr_1()            # SBR 1     (61 0)
    # Store the area in a register
    regx.append(roundn(x)) # 2nd Pause (36)
    x = mem[0]         # RCL 0     (33 0)
    # Call subroutine 1 to calculate the volume of a cube
    sbr_3()            # SBR 3     (61 0)
    # Store the volume in a register
    regx.append(roundn(x)) # 2nd Pause (36)
    x = mem[1]         # RCL 1     (33 0)
    # Call subroutine 1 to calculate the area of a circle
    sbr_2()            # SBR 2     (61 0)
    # Store the area in a register
    regx.append(roundn(x)) # 2nd Pause (36)
    x = mem[1]         # RCL 1     (33 0)
    # Call subroutine 1 to calculate the volume of a sphere
    sbr_4()            # SBR 4     (61 0)
    # Store the volume in a register
    regx.append(roundn(x)) # 2nd Pause (36)
    raise Stop()       # R/S       (81)
    


# Subroutine 1: area of a square
@with_goto
def sbr_1():
    global ee, mem, rounding, stack, unit, x
    label .label_1     # 2nd lbl 1 (86 0)
    # side x2
    x *= x             # x2        (23)
    return             # INV SBR   (- 61)
    


# Subroutine 2: area of a circle
@with_goto
def sbr_2():
    global ee, mem, rounding, stack, unit, x
    label .label_2     # 2nd Lbl 2 (86 0)
    # π x radius²
    x *= x             # x2        (23)
    stack.append(x)    # X         (55)
    x = pi             # 2nd pi    (30)
    y = stack.pop()    # =         (85)
    x = y * x
    return             # INV SBR   (- 61)
    


# Subroutine 3: volume of a cube
@with_goto
def sbr_3():
    global ee, mem, rounding, stack, unit, x
    label .label_3     # 2nd Lbl 3 (86 0)
    # side^3
    stack.append(x)    # y^x       (35)
    x = 3              # 3
    y = stack.pop()    # =         (85)
    x = pow(y, x)
    return             # INV SBR   (- 61)
    


# Subroutine 4: volume of a sphere
@with_goto
def sbr_4():
    global ee, mem, rounding, stack, unit, x
    label .label_4     # 2nd Lbl 4 (86 0)
    # 4/3π x radius^3
    stack.append(x)    # y^x       (35)
    x = 3              # 3
    y = stack.pop()    # X         (55)
    x = pow(y, x)
    stack.append(x)
    x = 4              # 4
    y = stack.pop()    # /         (45)
    x = y * x
    stack.append(x)
    x = 3              # 3
    y = stack.pop()    # X         (55)
    x = y / x
    stack.append(x)
    x = pi             # 2nd pi    (30)
    y = stack.pop()    # =         (85)
    x = y * x
    return             # INV SBR   (- 61)
