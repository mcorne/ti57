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
    # The same birthday
    
    # What is the probability that two or more people have the same birthday in a group of five?
    # Tip: this is actually 1 minus the probability that no one has the same birthday.
    # For example, we'll have 2.7% chance in a group of 5 people and 56.9% in a group of 25.
    # That is 1 - 364/365 X 363/365 X 362/365 X 361/365 for a group of 5 people.
    
    # Source: Training with your EC-4000 Programmable Calculator by Texas Instruments, 1977, page 6-6
    # https://1drv.ms/b/s!ArcO_mFRe1Z9yia_fdpsnBaOeEXc?e=uCJpdM
    
    # Input
    # Enter the number of people
    x = 5              # 5
    
    # Main program
    rounding = 1       # 2nd Fix 1 (48)
    # Max number of loops
    stack.append(x)    # -         (65)
    x = 1              # 1
    y = stack.pop()    # =         (85)
    x = y - x
    # Store in memory 7
    y = mem[7]         # x<>t      (22)
    mem[7] = x
    x = y
    x = 365            # 365
    mem[2] = x         # STO 2     (32 0)
    # Initial probability
    x = 1              # 1
    mem[3] = x         # STO 3     (32 0)
    # Number of loops
    x = 0              # 0
    mem[4] = x         # STO 4     (32 0)
    label .label_1     # 2nd Lbl 1 (86 0)
    # Ex. 363
    x = mem[2]         # RCL 2     (33 0)
    stack.append(x)    # -         (65)
    x = 1              # 1
    y = stack.pop()    # =         (85)
    x = y - x
    # Ex. 363/365
    mem[2] = x         # STO 2     (32 0)
    stack.append(x)    # /         (45)
    x = 365            # 365
    y = stack.pop()    # =         (85)
    x = y / x
    # Multiply to probability
    mem[3] *= x        # 2nd PRod 3 (39 0)
    # Add one loop
    x = 1              # 1
    mem[4] += x        # SUM 4     (34 0)
    x = mem[4]         # RCL 4     (33 0)
    # Is different from max loops ?
    if x != mem[7]:    # Inv 2nd x=t (- 66)
        # Yes, go for another loop
        goto .label_1  # GTO 1     (51 0)
    # 1 - probability
    x = 1              # 1
    stack.append(x)    # -         (65)
    x = mem[3]         # RCL 3     (33 0)
    y = stack.pop()    # =         (85)
    x = y - x
    # Convert to %
    stack.append(x)    # X         (55)
    x = 100            # 100
    y = stack.pop()    # =         (85)
    x = y * x
    raise Stop()       # R/S       (81)
