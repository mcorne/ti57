import re
from parser import Parser

from ti57 import instruction_set


class Generator:
    CODE = """
import internal_functions
init_calculator()

{}

return calculator_state()
"""

    SUBROUTINE = """
    def sbr_{}():            # {}"
        {}
"""

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

    def action_decrement_skip_on_zero(self):
        self.lines.append("sto[0] = math.floor(sto[0])")
        self.lines.append("if sto[0] > 0:")
        self.lines.append("    sto[0] -= 1")
        self.lines.append("elif sto[0] < 0:")
        self.lines.append("    sto[0] += 1")
        self.lines.append("")
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

    def add_subroutines(self, code):
        return code  # TODO: rename subroutine label to function def, shift code 4 spaces to the right !!!

        numbers = re.findall(r"sbr_([0-9]]+)", code, re.A)

        for number in numbers:
            match = re.search(
                f"label .label_{number}: +# +([^\n]+)(.+? +# INV SBR [^\n]+)",
                code,
                re.S,
            )
            # TODO: fix use of match !!!

            if match == None:
                raise Exception("No label found for SBR " + number)

            code = code.replace(match[0], "")
            subroutine = Generator.SUBROUTINE.format(number, match[1], match[2])
            code = subroutine + code

        return code

    def generate_code(self, instructions):
        code = self.process_instructions(instructions)
        code = self.add_subroutines(code)
        return Generator.CODE.format(code)

    def process_instructions(self, instructions):
        self.operators = []
        is_statement_group = False
        code = []
        parser = Parser(instructions, instruction_set)
        for self.instruction in parser.next_instruction():
            self.lines = []
            action = getattr(self, "action_" + self.instruction["action"])
            action()

            if not self.lines:
                self.lines.append("")

            ti_code = (
                self.instruction["ti_code"] if "ti_code" in self.instruction else ""
            )
            self.lines[
                0
            ] = f"{self.lines[0]: <27} # {self.instruction['value']: <12} #{self.instruction['step']: <2} {ti_code}"

            if is_statement_group:
                # TODO: indent statements 4 spaces
                self.lines.append("")
                is_statement_group = False

            if "python" in self.instruction:
                is_statement_group = self.instruction["python"][-1] == ":"

            code.append("\n".join(self.lines))

        return "\n".join(code)

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


instructions = """
    500 STO 1
    0.015 STO 2
    3 STO 3
    RCL 1 *
    ( RCL 2 /
    ( 1 - ( 1 + RCL 2 )
    Y^X RCL 3 +/- ) ) =
    45 2nd sin =
    """
g = Generator()
code = g.generate_code(instructions)
print(code)
