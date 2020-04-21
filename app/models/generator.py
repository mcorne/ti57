import re

from app.models.parser import Parser
from app.models.ti57 import instruction_set


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
        self.lines.append(f"y = sto[{self.instruction['number']}]")
        self.lines.append(f"sto[{self.instruction['number']}] = x")
        self.lines.append("x = y")

    def action_multiplication(self):
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        self.lines.append(f"x = {self.instruction['value']}")

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
        if self.instruction["python"] is list:
            self.lines += self.instruction["python"]
        else:
            self.lines.append(self.instruction["python"])

    def action_rectangular_to_polar(self):
        self.lines.append("y = x")
        self.lines.append("x = rad2unit(math.atan2(y, sto[7]))")
        self.lines.append("sto[7] = math.sqrt(sto[7] * sto[7] + y * y)")

    def action_scientific_notation(self):
        self.lines.append("ee = True")
        self.add_operation()

    def action_sum_minus(self):
        self.lines.append("sto[0] -= 1")  # population
        self.lines.append("sto[1] -= x")  # sum Y
        self.lines.append("sto[2] -= x * x")  # sum Y * Y
        self.lines.append("sto[3] -= sto[7]")  # sum X
        self.lines.append("sto[4] -= sto[7] * sto[7]")  # sum X * X
        self.lines.append("sto[5] -= sto[7] * x")  # sum X * Y
        self.lines.append("sto[7] -= 1")

    def action_sum_plus(self):
        self.lines.append("sto[0] += 1")  # population
        self.lines.append("sto[1] += x")  # sum Y
        self.lines.append("sto[2] += x * x")  # sum Y * Y
        self.lines.append("sto[3] += sto[7]")  # sum X
        self.lines.append("sto[4] += sto[7] * sto[7]")  # sum X * X
        self.lines.append("sto[5] += sto[7] * x")  # sum X * Y
        self.lines.append("sto[7] += 1")

    def add_function(self, lines, subroutine_numbers, line, fixed):
        label_number = self.get_label_number(line)
        if label_number not in subroutine_numbers:
            fixed.append(line)
        else:
            comments = self.extract_last_comments(fixed)
            fixed += [
                "",
                "",
                *comments,
                "@with_goto",
                f"def sbr_{label_number}():",
                "global ee, reg, rounding, sto, unit, x",
                line,
            ]

    def add_functions(self, lines, subroutine_numbers):
        fixed = []
        for line in lines:
            self.add_function(lines, subroutine_numbers, line, fixed)
        return fixed

    def add_operation(self):
        self.lines.append("reg.append(x)")
        self.operators.append(self.instruction["type"])

    def convert_instructions_to_code_lines(self, instructions):
        parser = Parser(instructions, instruction_set)
        for self.instruction in parser.next_instruction():
            number = len(self.lines)
            if self.instruction["action"]:
                action = getattr(self, "action_" + self.instruction["action"])
                action()
            if len(self.lines) == number:  # No python code added, ex. "INV SBR"
                self.lines.append("")
            if self.instruction["action"] != "comment":
                line = f"{self.lines[number]: <27} # {self.instruction['value']: <12} #{self.instruction['step']: <2}"
                self.lines[number] = line
                if "ti_code" in self.instruction:
                    self.lines[number] += " # " + self.instruction["ti_code"]

        return self.lines

    def extract_last_comments(self, lines):
        comments = []
        for line in reversed(lines):
            if line and line[0] != "#":
                break
            comments.insert(0, line)
            lines.pop()
        return comments

    def extract_subroutine_numbers(self, lines):
        subroutine_numbers = []
        for line in lines:
            subroutine_number = self.get_subroutine_number(line)
            if subroutine_number:
                subroutine_numbers.append(subroutine_number)
        return subroutine_numbers

    def generate_code(self, instructions):
        lines = self.convert_instructions_to_code_lines(instructions)
        self.indent_if_statement(lines)
        subroutine_numbers = self.extract_subroutine_numbers(lines)
        if subroutine_numbers:
            lines = self.add_functions(lines, subroutine_numbers)
        self.indent_lines(lines)

        with open("app/models/calculator.py", "r") as file:
            calculator = file.read()

        calculator += "\n".join(lines)

        return calculator

    def get_label_number(self, line):
        match = re.match(r"label .label_(\d)", line)
        if match:
            return match.group(1)

    def get_subroutine_number(self, line):
        match = re.match(r"sbr_(\d)", line)
        if match:
            return match.group(1)

    def indent_lines(self, lines):
        preceedes_def = False
        last = len(lines) - 1
        for number, line in enumerate(reversed(lines)):
            if not line:
                # This is a blank line, typically preceeding a function definition
                preceedes_def = False
            elif line[0:3] == "def":
                # This is a function definition
                preceedes_def = True
            elif not preceedes_def:
                # This is any line of code
                lines[last - number] = "    " + line
            # Else this is a comment or the "with_goto" decorator preceeding the function definition

    def indent_if_statement(self, lines):
        follows_if_statement = False
        for number, line in enumerate(lines):
            if not line:
                # Ignore empty lines
                continue
            if follows_if_statement:
                # This is a line following an "if" statement
                if self.is_if_statement(line):
                    raise Exception('Nested "if" statements not allowed: {line}')
                # Ident the line and move the instruction part to the left
                lines[number] = "    " + line.replace("    #", "#", 1)
                if line[0] != "#":
                    # This is the line of code, the end of the "if" statement
                    follows_if_statement = False
                # Else this is a comment line and not yet the line of code following the "if" statement
            elif self.is_if_statement(line):
                follows_if_statement = True

    def is_end_subroutine(self, line):
        return bool(re.match(r" +# INV +SBR", line, re.I))

    def is_if_statement(self, line):
        return line and (line[0:2] == "if" or line[0:4] == "elif")

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
