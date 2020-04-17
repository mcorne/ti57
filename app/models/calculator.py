import math
import re


class Calculator:
    def __init__(self):
        self.ee = False  # Disable scientific notation
        self.reg = []  # Reset internal registers
        self.rounding = None  # Disable rounding of numbers
        self.sto = [0 for i in range(8)]  # Reset memory
        self.unit = "Deg"  # Set degree mode
        self.x = 0  # Reset display

    def degrees2dms(self, degrees):
        is_positive = degrees >= 0
        if not is_positive:
            degrees = -degrees

        int_degrees = int(degrees)
        remainder = (float(degrees) - int_degrees) * 60
        minutes = int(remainder)
        seconds = (remainder - minutes) * 60

        dms = float(f"{int_degrees}.{minutes}{seconds}")
        if not is_positive:
            dms = -dms
        return dms

    def dms2degrees(self, dms):
        match = re.fullmatch(
            r"(?P<sign>[+-])?(?P<degrees>[0-9]+)\.?(?P<minutes>[0-9]{1,2})?(?P<seconds>[0-9]{1,2})?(?P<remainder>[0-9]*)",
            dms,
        )
        if match is None:
            raise Exception(f"Invalid DMS angle {dms}")

        angle = match.groupdict()
        degrees = float(angle["degrees"])

        if "minutes" in angle:
            if len(angle["minutes"]) == 1:
                angle["minutes"] += 0
            degrees += float(angle["minutes"]) / 60

        if "seconds" in angle:
            if len(angle["seconds"]) == 1:
                angle["seconds"] += 0
            degrees += float(angle["seconds"]) / 3600

        if "remainder" in angle:
            degrees += float("0." + angle["remainder"]) / 3600

        if "sign" in angle and angle["sign"] == "-":
            degrees = -degrees
        return degrees

    def get_state(self):
        rounded = self.x if self.rounding is None else round(self.x, self.rounding)
        state = {
            "ee": self.ee,
            "reg": self.reg,
            "rounded": rounded,
            "rounding": self.rounding,
            "sto": self.sto,
            "unit": self.unit,
            "x": self.x,
        }
        return state

    def grd2rad(self, number):
        return (number / 200) * math.pi

    def rad2grd(self, number):
        return (number / math.pi) * 200

    def rad2unit(self, number):
        number = float(number)
        if self.unit == "Deg":
            number = math.degrees(number)
        elif self.unit == "Grd":
            number = self.rad2grd(number)
        return number

    def unit2rad(self, number):
        number = float(number)
        if self.unit == "Deg":
            number = math.radians(number)
        elif self.unit == "Grd":
            number = self.grd2rad(number)
        return number
