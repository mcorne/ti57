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

    def dms2degrees(self, dms):
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
