import re
from parser import Parser


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
        self.code_line = []
        self.operators = []
        self.prev_operator = None
        self.token = {}

    def action_addition(self):
        self.process_prev_equality()
        self.add_operation()

    def action_clear(self):
        self.code_line.append("x = 0")
        self.code_line.append("ee = False")
        self.code_line.append("reg = []")

        self.operators = []
        self.prev_operator = None

    def action_clear_all(self):
        self.action_clear()
        self.code_line.append("sto = [0 for i in range(8)]")

    def action_closing_parenthesis(self):
        self.process_prev_equality()

        if self.prev_operator != "(":
            raise Exception("Unexpected closing parenthesis")

        self.operators.pop()

    def action_decrement_skip_on_zero(self):
        self.code_line.append("sto[0] = math.floor(sto[0])")
        self.code_line.append("if sto[0] > 0:")
        self.code_line.append("    sto[0] -= 1")
        self.code_line.append("elif sto[0] < 0:")
        self.code_line.append("    sto[0] += 1")
        self.code_line.append("")
        self.code_line.append(self.token["statement"])

    def action_equality(self):
        self.process_prev_equality()

    def action_exchange_memory(self):
        self.code_line.append("y = sto[{}]".format(self.token["number"]))
        self.code_line.append("sto[{}] = x".format(self.token["number"]))
        self.code_line.append("x = y")

    def action_multiplication(self):
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        self.code_line.append("x = {}".format(self.token["value"]))

    def action_open_parenthesis(self):
        self.code_line.append("")
        self.operators.append(self.token["type"])

    def action_polar_to_rectangular(self):
        self.code_line.append("t = x")
        self.code_line.append("y = unit2rad(t)")
        self.code_line.append("x = sto[7] * math.sin(y)")
        self.code_line.append("sto[7] = sto[7] * math.cos(y)")

    def action_power(self):
        self.process_prev_power()
        self.add_operation()

    def action_python_code(self):
        self.code_line.append(self.token["statement"])

    def action_rectangular_to_polar(self):
        self.code_line.append("y = x")
        self.code_line.append("x = rad2unit(math.atan2(y, sto[7]))")
        self.code_line.append("sto[7] = math.sqrt(sto[7] * sto[7] + y * y)")

    def action_scientific_notation(self):
        self.code_line.append("ee = True")
        self.add_operation()

    def action_sum(self):
        self.code_line.append("sto[0] += 1")  # population
        self.code_line.append("sto[1] += x")  # sum Y
        self.code_line.append("sto[2] += x * x")  # sum Y * Y
        self.code_line.append("sto[3] += sto[7]")  # sum X
        self.code_line.append("sto[4] += sto[7] * sto[7]")  # sum X * X
        self.code_line.append("sto[5] += sto[7] * x")  # sum X * Y
        self.code_line.append("sto[7] += 1")

    def add_operation(self):
        self.code_line.append("reg.append(x)")
        self.operators.append(self.token["type"])

    def add_subroutines(self, code):
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

    def generate_code(self, code):
        code_lines = self.process_tokens(code)
        code = self.implode_code_lines(code_lines)
        code = self.add_subroutines(code)

        return Generator.CODE.format(code)

    def implode_code_lines(self, code_lines):
        code_lines = ["\n".join(subset) for subset in code_lines]
        return "\n".join(code_lines)

    def process_prev_equality(self):
        self.process_prev_multiplication()

        if self.prev_operator == "+" or self.prev_operator == "-":
            self.operators.pop()
            self.code_line.append("y = reg.pop()")
            self.code_line.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_multiplication(self):
        self.process_prev_power()

        if self.prev_operator == "*" or self.prev_operator == "/":
            self.operators.pop()
            self.code_line.append("y = reg.pop()")
            self.code_line.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_power(self):
        self.process_prev_scientific_notation()

        if self.prev_operator == "power" or self.prev_operator == "root":
            self.operators.pop()
            self.code_line.append("y = reg.pop()")
            exponent_sign = "-" if self.prev_operator == "root" else ""
            self.code_line.append(f"x = math.pow(y, {exponent_sign}x)")
            self.update_prev_operator()

    def process_prev_scientific_notation(self):
        self.update_prev_operator() if self.operators else None

        if self.prev_operator == "EE":
            self.operators.pop()
            self.code_line.append("y = reg.pop()")
            self.code_line.append("x = y * math.pow(10, x)")
            self.update_prev_operator()

    def process_tokens(self, code):
        self.operators = []
        is_statement_group = False
        code_lines = []
        parser = Parser(code)
        for self.token in parser.next_token():
            self.code_line = []
            action = getattr(self, "action_" + self.token["action"])
            action()

            if not self.code_line:
                self.code_line.append("")

            ti_code = self.token["ti_code"] if "ti_code" in self.token else ""
            self.code_line[
                0
            ] = f"{self.code_line[0]: <27} # {self.token['value']: <12} #{self.token['step']: <2} {ti_code}"

            if is_statement_group:
                # TODO: indent statements 4 spaces
                self.code_line.append("")
                is_statement_group = False

            if "statement" in self.token:
                is_statement_group = self.token["statement"][-1] == ":"

            code_lines.append(self.code_line)

        return code_lines

    def update_prev_operator(self):
        self.prev_operator = self.operators[-1] if self.operators else None


code = """
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
python_code = g.generate_code(code, False)
print(python_code)
