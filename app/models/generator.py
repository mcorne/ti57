import re

from app.models.parser import Parser
from app.models.ti57 import instruction_set


class Generator:
    def __init__(self):
        self.py_lines = []
        self.operators = []
        self.prev_operator = None
        self.ti_instruction = {}

    def action_addition(self):
        self.process_prev_equality()
        self.add_operation()

    def action_clear(self):
        self.py_lines.append("x = 0")
        self.py_lines.append("ee = False")
        self.py_lines.append("reg = []")

        self.operators = []
        self.prev_operator = None

    def action_clear_all(self):
        self.action_clear()
        self.py_lines.append("sto = [0 for i in range(8)]")

    def action_closing_parenthesis(self):
        self.process_prev_equality()

        if self.prev_operator != "(":
            raise Exception("Unexpected closing parenthesis")

        self.operators.pop()

    def action_comment(self):
        self.py_lines.append(self.ti_instruction["value"])

    def action_equality(self):
        self.process_prev_equality()

    def action_multiplication(self):
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        self.py_lines.append(f"x = {self.ti_instruction['value']}")

    def action_open_parenthesis(self):
        self.py_lines.append("")
        self.operators.append(self.ti_instruction["type"])

    def action_power(self):
        self.process_prev_power()
        self.add_operation()

    def action_py_line(self):
        if type(self.ti_instruction["py_line"]) is list:
            self.py_lines += self.ti_instruction["py_line"]
        else:
            self.py_lines.append(self.ti_instruction["py_line"])

    def action_scientific_notation(self):
        self.py_lines.append("ee = True")
        self.add_operation()

    def add_function(self, py_lines, subroutine_numbers, py_line, fixed):
        label_number = self.get_label_number(py_line)
        if label_number not in subroutine_numbers:
            fixed.append(py_line)
        else:
            comments = self.extract_last_comments(fixed)
            fixed += [
                "",
                "",
                *comments,
                "@with_goto",
                f"def sbr_{label_number}():",
                "global ee, reg, rounding, sto, unit, x",
                py_line,
            ]

    def add_functions(self, py_lines, subroutine_numbers):
        fixed = []
        for py_line in py_lines:
            self.add_function(py_lines, subroutine_numbers, py_line, fixed)
        return fixed

    def add_operation(self):
        self.py_lines.append("reg.append(x)")
        self.operators.append(self.ti_instruction["type"])

    def convert_ti_instructions_to_py_lines(self, ti_instructions):
        parser = Parser(ti_instructions, instruction_set)
        for self.ti_instruction in parser.next_instruction():
            number = len(self.py_lines)
            if self.ti_instruction["action"]:
                action = getattr(self, "action_" + self.ti_instruction["action"])
                action()
            if len(self.py_lines) == number:  # No python line added, ex. "INV SBR"
                self.py_lines.append("")
            if self.ti_instruction["action"] != "comment":
                py_line = f"{self.py_lines[number]: <27} # {self.ti_instruction['value']: <12} #{self.ti_instruction['step']: <2}"
                self.py_lines[number] = py_line
                if "ti_code" in self.ti_instruction:
                    self.py_lines[number] += " # " + self.ti_instruction["ti_code"]

        return self.py_lines

    def extract_last_comments(self, py_lines):
        comments = []
        for py_line in reversed(py_lines):
            if py_line and py_line[0] != "#":
                break
            comments.insert(0, py_line)
            py_lines.pop()
        return comments

    def extract_subroutine_numbers(self, py_lines):
        subroutine_numbers = []
        for py_line in py_lines:
            subroutine_number = self.get_subroutine_number(py_line)
            if subroutine_number:
                subroutine_numbers.append(subroutine_number)
        return subroutine_numbers

    def generate_py_code(self, ti_instructions):
        py_lines = self.convert_ti_instructions_to_py_lines(ti_instructions)
        self.indent_if_statement(py_lines)
        subroutine_numbers = self.extract_subroutine_numbers(py_lines)
        if subroutine_numbers:
            py_lines = self.add_functions(py_lines, subroutine_numbers)
        self.indent_lines(py_lines)

        with open("app/models/calculator.py", "r") as file:
            calculator = file.read()

        calculator += "\n".join(py_lines)

        return calculator

    def get_label_number(self, py_line):
        match = re.match(r"label .label_(\d)", py_line)
        if match:
            return match.group(1)

    def get_subroutine_number(self, py_line):
        match = re.match(r"sbr_(\d)", py_line)
        if match:
            return match.group(1)

    def indent_lines(self, py_lines):
        preceedes_def = False
        last = len(py_lines) - 1
        for number, py_line in enumerate(reversed(py_lines)):
            if not py_line:
                # This is a blank line, typically preceeding a function definition
                preceedes_def = False
            elif py_line[0:3] == "def":
                # This is a function definition
                preceedes_def = True
            elif not preceedes_def:
                # This is any line of code
                py_lines[last - number] = "    " + py_line
            # Else this is a comment or the "with_goto" decorator preceeding the function definition

    def indent_if_statement(self, py_lines):
        follows_if_statement = False
        for number, py_line in enumerate(py_lines):
            if not py_line:
                # Ignore empty py_lines
                continue
            if follows_if_statement:
                # This is a line following an "if" statement
                if self.is_if_statement(py_line):
                    raise Exception('Nested "if" statements not allowed: {py_line}')
                # Ident the line and move the instruction part to the left
                py_lines[number] = "    " + py_line.replace("    #", "#", 1)
                if py_line[0] != "#":
                    # This is the line of code, the end of the "if" statement
                    follows_if_statement = False
                # Else this is a comment line and not yet the py_line of code following the "if" statement
            elif self.is_if_statement(py_line):
                follows_if_statement = True

    def is_end_subroutine(self, py_line):
        return bool(re.match(r" +# INV +SBR", py_line, re.I))

    def is_if_statement(self, py_line):
        return py_line and (py_line[0:2] == "if" or py_line[0:4] == "elif")

    def process_prev_equality(self):
        self.process_prev_multiplication()

        if self.prev_operator == "+" or self.prev_operator == "-":
            self.operators.pop()
            self.py_lines.append("y = reg.pop()")
            self.py_lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_multiplication(self):
        self.process_prev_power()

        if self.prev_operator == "*" or self.prev_operator == "/":
            self.operators.pop()
            self.py_lines.append("y = reg.pop()")
            self.py_lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_power(self):
        self.process_prev_scientific_notation()

        if self.prev_operator == "power" or self.prev_operator == "root":
            self.operators.pop()
            self.py_lines.append("y = reg.pop()")
            exponent_sign = "-" if self.prev_operator == "root" else ""
            self.py_lines.append(f"x = pow(y, {exponent_sign}x)")
            self.update_prev_operator()

    def process_prev_scientific_notation(self):
        self.update_prev_operator() if self.operators else None

        if self.prev_operator == "EE":
            self.operators.pop()
            self.py_lines.append("y = reg.pop()")
            self.py_lines.append("x = y * pow(10, x)")
            self.update_prev_operator()

    def update_prev_operator(self):
        self.prev_operator = self.operators[-1] if self.operators else None
