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
# comment 1
# comment 2                 # 5            #3
x = 5                       # STO 4        #4  #   32 4
sto[4] = x
# comment 3                 # SBR 1        #6  #   61 1
sbr_1()
# func 1
# func 11
# func 111                  # 2nd Lbl 0    #10 #   86 0
label .label_0
# func 1111                 # 3            #12
x = 3                       # STO 4        #13 #   32 4
sto[4] = x                  # 2.5          #14
x = 2.5                     # +/-          #15 #   84
x = -x                      # STO 0        #16 #   32 0
sto[0] = x                  # 2nd Dsz      #17 #   56
sto[0] = math.floor(sto[0])
if sto[0] > 0:
sto[0] -= 1
elif sto[0] < 0:
sto[0] += 1
if sto[0] != 0:             # 4            #18
x = 4                       # 5            #19
x = 5                       # INV SBR      #20 # - 61
                            # 2nd Lbl 1    #21 #   86 1
label .label_1              # 2            #22
x = 2                       # STO 4        #23 #   32 4
sto[4] = x
# call 0
# call 00                   # SBR 0        #26 #   61 0
sbr_0()                     # INV SBR      #27 # - 61
