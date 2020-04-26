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
# History of values displayed before a pause (2nd pause)
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
    # Building a savings plan
    
    # Let's say you make a monthly deposit (PMT) of $55.
    # How much your cash will grow every month (n) at a 0.7% interest rate (i)?
    # Answer: $110.38 including $0.38 of earned interest after a the first full month.
    # Then $166.16 including $1.16 etc., and finally $686.01 including $26.01 after a year.
    # Tip! Amount = PMT X ((1+i)^n - 1) / i.
    
    # Source: Training with your EC-4000 Programmable Calculator by Texas Instruments, 1977, page 8-8
    # https://1drv.ms/b/s!ArcO_mFRe1Z9yia_fdpsnBaOeEXc?e=uCJpdM
    
    # Input
    # Monthly payment (PMT)
    x = 55             # 55
    mem[1] = x         # STO 1     (32 0)
    # Interest rate (i)
    x = 0.007          # 0.007
    mem[2] = x         # STO 2     (32 0)
    # Number of months
    x = 12             # 12
    mem[7] = x         # STO 7     (32 0)
    
    # Main program
    rounding = 2       # 2nd Fix 2 (48)
    # Month (n)
    x = 0              # 0
    mem[3] = x         # STO 3     (32 0)
    label .label_0     # 2nd Lbl 0 (86 0)
    # month + 1
    x = 1              # 1
    mem[3] += x        # SUM 3     (34 0)
    x = mem[3]         # RCL 3     (33 0)
    regx.append(roundn(x)) # 2nd Pause (36)
    # PMT X ((1+i)^n - 1) / i
    x = mem[1]         # RCL 1     (33 0)
    stack.append(x)    # X         (55)
                       # (         (43)
                       # (         (43)
    x = 1              # 1
    stack.append(x)    # +         (75)
    x = mem[2]         # RCL 2     (33 0)
    y = stack.pop()    # )         (44)
    x = y + x
    stack.append(x)    # y^x       (35)
    x = mem[3]         # RCL 3     (33 0)
    y = stack.pop()    # -         (65)
    x = pow(y, x)
    stack.append(x)
    x = 1              # 1
    y = stack.pop()    # )         (44)
    x = y - x
    y = stack.pop()    # /         (45)
    x = y * x
    stack.append(x)
    x = mem[2]         # RCL 2     (33 0)
    y = stack.pop()    # =         (85)
    x = y / x
    regx.append(roundn(x)) # 2nd Pause (36)
    stack.append(x)    # -         (65)
    x = mem[1]         # RCL 1     (33 0)
    stack.append(x)    # X         (55)
    x = mem[3]         # RCL 3     (33 0)
    y = stack.pop()    # =         (85)
    x = y * x
    y = stack.pop()
    x = y - x
    regx.append(roundn(x)) # 2nd Pause (36)
    x = mem[3]         # RCL 3     (33 0)
    # Month lower than number of months?
    if x < mem[7]:     # INV 2nd x>=t (- 76)
        # Yes, go back to the begining
        goto .label_0  # GTO 0     (51 0)
    # No, stop
    raise Stop()       # R/S       (81)
