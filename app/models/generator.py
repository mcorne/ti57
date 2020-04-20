import re
from parser import Parser

from ti57 import instruction_set


class Generator:
    def __init__(self):
        self.lines = []
        self.operators = []
        self.prev_operator = None
        self.instruction = {}

    def action_addition(self):
        self.process_prev_equality()
        self.add_operation()

    def action_clear(self):
        self.lines.append("x = 0")
        self.lines.append("ee = False")
        self.lines.append("reg = []")

        self.operators = []
        self.prev_operator = None

    def action_clear_all(self):
        self.action_clear()
        self.lines.append("sto = [0 for i in range(8)]")

    def action_closing_parenthesis(self):
        self.process_prev_equality()

        if self.prev_operator != "(":
            raise Exception("Unexpected closing parenthesis")

        self.operators.pop()

    def action_comment(self):
        self.lines.append(self.instruction["value"])

    def action_decrement_skip_on_zero(self):
        self.lines.append("sto[0] = math.floor(sto[0])")
        self.lines.append("if sto[0] > 0:")
        self.lines.append("sto[0] -= 1")
        self.lines.append("elif sto[0] < 0:")
        self.lines.append("sto[0] += 1")
        self.lines.append(self.instruction["python"])

    def action_equality(self):
        self.process_prev_equality()

    def action_exchange_memory(self):
        self.lines.append("y = sto[{}]".format(self.instruction["number"]))
        self.lines.append("sto[{}] = x".format(self.instruction["number"]))
        self.lines.append("x = y")

    def action_multiplication(self):
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        self.lines.append("x = {}".format(self.instruction["value"]))

    def action_open_parenthesis(self):
        self.lines.append("")
        self.operators.append(self.instruction["type"])

    def action_polar_to_rectangular(self):
        self.lines.append("t = x")
        self.lines.append("y = unit2rad(t)")
        self.lines.append("x = sto[7] * math.sin(y)")
        self.lines.append("sto[7] = sto[7] * math.cos(y)")

    def action_power(self):
        self.process_prev_power()
        self.add_operation()

    def action_python(self):
        self.lines.append(self.instruction["python"])

    def action_rectangular_to_polar(self):
        self.lines.append("y = x")
        self.lines.append("x = rad2unit(math.atan2(y, sto[7]))")
        self.lines.append("sto[7] = math.sqrt(sto[7] * sto[7] + y * y)")

    def action_scientific_notation(self):
        self.lines.append("ee = True")
        self.add_operation()

    def action_sum(self):
        self.lines.append("sto[0] += 1")  # population
        self.lines.append("sto[1] += x")  # sum Y
        self.lines.append("sto[2] += x * x")  # sum Y * Y
        self.lines.append("sto[3] += sto[7]")  # sum X
        self.lines.append("sto[4] += sto[7] * sto[7]")  # sum X * X
        self.lines.append("sto[5] += sto[7] * x")  # sum X * Y
        self.lines.append("sto[7] += 1")

    def add_operation(self):
        self.lines.append("reg.append(x)")
        self.operators.append(self.instruction["type"])

    def fix_subroutines(self, code):
        pattern = r"^    label .label_([0-9]+)(.+?)\n(.+?INV SBR)"
        replacement = r"""

@with_goto
def sbr_\g<1>():      \g<2>
    global ee, reg, rounding, sto, unit, x
\g<3>"""
        code = re.sub(pattern, replacement, code, 0, re.M | re.S)
        return code

    def fix_subroutines_top_comments(self, code):
        pattern = r"(^    #[^\n]*?\n)+\n+^@with_goto\ndef sbr"
        match = re.findall(pattern, code, re.M | re.S)

        replacement = r"\n\n\g<1>\n\g<2>"
        # code = re.sub(pattern, replacement, code, 0, re.M | re.S)

        return code

    def generate_code(self, instructions):
        lines = self.process_instructions(instructions)
        # code = self.indent_code(code)
        # code = self.fix_subroutines(code)
        # code = self.fix_subroutines_top_comments(code)

        with open("app/models/calculator.py", "r") as file:
            calculator = file.read()

        calculator += "\n".join(lines)

        return calculator

    def indent_code(self, code):
        return re.sub("^.+$", r"    \g<0>", code, 0, re.M)

    def indent_if_statement(self, lines):
        follows_if_statement = False
        for number, line in enumerate(lines):
            if follows_if_statement:
                # This is a line following an "if" statement, ident the line 4 spaces
                lines[number] = "    " + line
                if line[0:2] == "if":
                    raise Exception('Nested "if" statements not allowed: {line}')
                if line[0] != "#":
                    # This is the line of code, the end of the "if" statement
                    follows_if_statement = False
                # Else this is a comment line and not yet the line of code following the "if" statement
            elif line[0:2] == "if":
                follows_if_statement = True
        return lines

    def process_instructions(self, instructions):
        parser = Parser(instructions, instruction_set)
        for self.instruction in parser.next_instruction():
            count = len(self.lines)
            if self.instruction["action"]:
                action = getattr(self, "action_" + self.instruction["action"])
                action()
            if len(self.lines) == count:  # No python code added, ex. "INV SBR"
                self.lines.append("")
            if self.instruction["action"] != "comment":
                number = count - 1
                line = f"{self.lines[number]: <27} # {self.instruction['value']: <12} #{self.instruction['step']: <2}"
                self.lines[number] = line
                if "ti_code" in self.instruction:
                    self.lines[number] += " # " + self.instruction["ti_code"]

        return self.lines

    def process_prev_equality(self):
        self.process_prev_multiplication()

        if self.prev_operator == "+" or self.prev_operator == "-":
            self.operators.pop()
            self.lines.append("y = reg.pop()")
            self.lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_multiplication(self):
        self.process_prev_power()

        if self.prev_operator == "*" or self.prev_operator == "/":
            self.operators.pop()
            self.lines.append("y = reg.pop()")
            self.lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_power(self):
        self.process_prev_scientific_notation()

        if self.prev_operator == "power" or self.prev_operator == "root":
            self.operators.pop()
            self.lines.append("y = reg.pop()")
            exponent_sign = "-" if self.prev_operator == "root" else ""
            self.lines.append(f"x = math.pow(y, {exponent_sign}x)")
            self.update_prev_operator()

    def process_prev_scientific_notation(self):
        self.update_prev_operator() if self.operators else None

        if self.prev_operator == "EE":
            self.operators.pop()
            self.lines.append("y = reg.pop()")
            self.lines.append("x = y * math.pow(10, x)")
            self.update_prev_operator()

    def update_prev_operator(self):
        self.prev_operator = self.operators[-1] if self.operators else None


# instructions = """
#         500 STO 1
#         0.015 STO 2
#         3 STO 3
#         RCL 1 *
#         ( RCL 2 /
#         ( 1 - ( 1 + RCL 2 )
#         Y^X RCL 3 +/- ) ) =
#         45 2nd sin =
#         """

# instructions = """
#         10.25 EE 2 * 3 =
#         """

# instructions = """
#         1 y^x 2 y^x 3 INV y^x 4 y^x 5 =
#         """

# instructions = """
#         1 * 3 + 4 * 5 y^x 2 - 7 / 8 =
#         """

# instructions = """
#         2 y^x 3 / 2 =
#         """

# 27
# instructions = "(1+2) * (4+5) ="

# [x] => 4.916523412787E-10
# instructions = "1 * 2 / 3 y^x 4 y^x 5 * 6 / 7 ="

# instructions = """
#         90 2nd sin =
#         +/- INV 2nd cos =
#         """

# instructions = """
#         5 STO 7
#         2 2nd Exc 7
#         RCL 7
#         """

# instructions = """
#         5 STO 7
#         2 x<>t
#         RCL 7
#         """

# instructions = """
#         5 STO 7
#         2 + 3 * ( 5 + 6
#         CLR
#         1+2=
#         RCL 7
#         """

# instructions = "5 STO 1 INV 2nd Ct RCL 1"

# instructions = """
#         45.153030 +/-
#         2nd D.MS
#         """

# instructions = """
#         45.153030
#         2nd D.MS
#         INV 2nd D.MS
#         """

# instructions = "10 x<>t 120 2nd P->R x<>t"

# instructions = """
#         3 2nd Fix
#         1 x<>t 2 +/- INV 2nd P->R x<>t
#         """

# instructions = "2nd pi 2nd Int "
# instructions = "2nd pi INV 2nd Int"

# instructions = """
#         2.5 +/- STO 0
#         2nd Dsz
#         4
#         5
#         """

# instructions = """
#         1 STO 7
#         2
#         2nd x=t
#         3
#         4
#         """

# instructions = """
#         2 x<>t 10 2nd S+
#         3 x<>t 20 2nd S+
#         5 x<>t 30 2nd S+
#         6 x<>t 40 2nd S+
#         10 x<>t 2 2nd S+
#         INV 2nd x
#         2nd x
#         INV 2nd s2
#         2nd s2
#         """

instructions = """
        # comment 1
        # comment 2
        5 STO 4
        # comment 3
        SBR 1
        # func 1
        # func 11
        # func 111
        2nd Lbl 0
        # func 1111
        3 STO 4
        2.5 +/- STO 0
        2nd Dsz
        4
        5
        INV SBR
        2nd Lbl 1
        2 STO 4
        # call 0
        # call 00
        SBR 0
        INV SBR
        """

g = Generator()
# code = g.generate_code(instructions)
# with open("app/models/test.py", "w") as file:
#     file.write(code)
# print(code)
# exec(code)
# main()
# print(state())
print(g.indent_if_statement(["aaa", "if qsd:", "#eee", "#rrr", "ttt", "yyy", "uuu",]))
