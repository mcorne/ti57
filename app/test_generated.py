import math
import re

from goto import with_goto

ee = False  # Disable scientific notation
reg = []  # Reset internal registers
rounding = None  # Disable rounding of numbers
sto = [0 for i in range(8)]  # Reset memory
unit = "Deg"  # Set degree mode
x = 0  # Reset display


def degrees2dms(degrees):
    degrees = float(degrees)
    is_positive = degrees >= 0
    if not is_positive:
        degrees = -degrees

    minutes, seconds = divmod(degrees * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    # Internal mantissa has 11 digits on TI-57 and 13 on TI-59
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
    return (number / 200) * math.pi


def rad2grd(number):
    return (number / math.pi) * 200


def rad2unit(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = math.degrees(number)
    elif unit == "Grd":
        number = rad2grd(number)
    return number


def state():
    global ee, reg, rounding, sto, unit, x
    rounded = x if rounding is None else round(x, rounding)
    state = {
        "ee": ee,
        "reg": reg,
        "rounded": rounded,
        "rounding": rounding,
        "sto": sto,
        "unit": unit,
        "x": x,
    }
    return state


def unit2rad(number):
    global unit
    number = float(number)
    if unit == "Deg":
        number = math.radians(number)
    elif unit == "Grd":
        number = grd2rad(number)
    return number


@with_goto
def main():
    global ee, reg, rounding, sto, unit, x
    label.label_rst
    x = 2                       # 2            #1 
    y = sto[7]                  # x<>t         #2  #   22
    sto[7] = x
    x = y
    x = 10                      # 10           #3 
    sto[0] += 1                 # 2nd S+       #4  #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = 3                       # 3            #5 
    y = sto[7]                  # x<>t         #6  #   22
    sto[7] = x
    x = y
    x = 20                      # 20           #7 
    sto[0] += 1                 # 2nd S+       #8  #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = 5                       # 5            #9 
    y = sto[7]                  # x<>t         #10 #   22
    sto[7] = x
    x = y
    x = 30                      # 30           #11
    sto[0] += 1                 # 2nd S+       #12 #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = 6                       # 6            #13
    y = sto[7]                  # x<>t         #14 #   22
    sto[7] = x
    x = y
    x = 40                      # 40           #15
    sto[0] += 1                 # 2nd S+       #16 #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = 10                      # 10           #17
    y = sto[7]                  # x<>t         #18 #   22
    sto[7] = x
    x = y
    x = 2                       # 2            #19
    sto[0] += 1                 # 2nd S+       #20 #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = 10                      # 10           #21
    y = sto[7]                  # x<>t         #22 #   22
    sto[7] = x
    x = y
    x = 2                       # 2            #23
    sto[0] -= 1                 # INV 2nd S+   #24 # - 88
    sto[1] -= x
    sto[2] -= x * x
    sto[3] -= sto[7]
    sto[4] -= sto[7] * sto[7]
    sto[5] -= sto[7] * x
    sto[7] -= 1
    x = 10                      # 10           #25
    y = sto[7]                  # x<>t         #26 #   22
    sto[7] = x
    x = y
    x = 2                       # 2            #27
    sto[0] += 1                 # 2nd S+       #28 #   88
    sto[1] += x
    sto[2] += x * x
    sto[3] += sto[7]
    sto[4] += sto[7] * sto[7]
    sto[5] += sto[7] * x
    sto[7] += 1
    x = sto[3] / sto[0]         # INV 2nd x    #29 # - 89
    x = sto[1] / sto[0]         # 2nd x        #30 #   89
    x = (sto[4] - sto[3] * sto[3] / sto[0]) / sto[0] # INV 2nd s2   #31 # - 80
    x = (sto[2] - sto[1] * sto[1] / sto[0]) / sto[0] # 2nd s2       #32 #   80