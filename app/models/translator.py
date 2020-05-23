import re

from flask import current_app

from app.models.parser import Parser
from app.models.ti57 import instruction_set


class Translator:
    """Translation of TI instructions into Python."""

    # Python line length:
    # Median = 14 (ex. "if mem[0] > 0:")
    # Q3     = 18 (ex. "x = degrees2dms(x)")
    # Max    = 48 (ex. "x = (mem[4] - mem[3] * mem[3] / mem[0]) / mem[0]")
    PY_LINE_LENGTH = 22
    # TI instruction length:
    # Median = 7 (ex. "2nd Dsz")
    # Q3     = 9 (ex. "2nd Exc 0")
    # Max    = 13 (ex. "INV 2nd Prd 0")
    TI_INSTRUCTION_LENGTH = 9

    def __init__(self):
        self.py_lines = []
        self.operators = []
        self.prev_operator = None
        self.ti_instruction = {}

    def action_addition(self):
        """Process the + operator."""
        self.process_prev_equality()
        self.add_operation()

    def action_clear(self):
        """Process the CLR key."""
        self.py_lines.append("x = 0")
        self.py_lines.append("ee = False")
        self.py_lines.append("stack = []")

        self.operators = []
        self.prev_operator = None

    def action_clear_all(self):
        """Process the INV 2nd Ct key."""
        self.action_clear()
        self.py_lines.append("mem = [0 for i in range(8)]")

    def action_closing_parenthesis(self):
        """Process the ) character."""
        self.process_prev_equality()
        if self.prev_operator != "(":
            raise Exception("Syntax error: unexpected closing parenthesis")
        self.operators.pop()
        self.update_prev_operator()

    def action_comment(self):
        """Process a comment line (starting with #)."""
        self.py_lines.append(self.ti_instruction["value"])

    def action_equality(self):
        """Process the = sign."""
        self.process_prev_equality()

    def action_multiplication(self):
        """Process the X operator."""
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        """Process a number."""
        self.py_lines.append(f"x = {self.ti_instruction['value']}")

    def action_opening_parenthesis(self):
        """Process the ( character."""
        self.py_lines.append("")
        self.operators.append(self.ti_instruction["type"])

    def action_power(self):
        """Process the y^x key."""
        self.process_prev_power()
        self.add_operation()

    def action_py_line(self):
        """Adds one or more Python lines of code corresponding to a key."""
        if type(self.ti_instruction["py_line"]) is list:
            self.py_lines += self.ti_instruction["py_line"]
        else:
            self.py_lines.append(self.ti_instruction["py_line"])

    def action_scientific_notation(self):
        """Process the EE key (within a number)."""
        self.py_lines.append("ee = True")
        self.add_operation()

    def add_end_labels(self, py_lines):
        """Add an end label to each function."""
        is_function_end = True
        last = len(py_lines) - 1
        for number, py_line in enumerate(reversed(py_lines)):
            if py_line and py_line[0] != "#":
                # This is not a blank line or a comment
                if py_line[0:3] == "def":
                    # This is a function definition
                    is_function_end = True
                elif is_function_end:
                    if "goto .end" in py_line:
                        # This is the last "INV SBR" (the end of the subroutine), replace the goto with the label
                        py_lines[last - number] = py_line.replace(
                            "goto .end ", "label .end"
                        )
                        is_function_end = False
                    elif "raise UserWarning('R/S')" in py_line:
                        # This is a subroutine finishing with "R/S", add the label
                        py_lines[last - number] += "\n    label .end"
                        is_function_end = False

    def add_function(self, py_lines, subroutine_numbers, py_line, fixed):
        """Add the function definition of a subroutine."""
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
                "global ee, mem, rounding, stack, unit, x",
                py_line,
            ]

    def add_functions(self, py_lines, subroutine_numbers):
        """Process subroutines."""
        fixed = []
        for py_line in py_lines:
            self.add_function(py_lines, subroutine_numbers, py_line, fixed)
        return fixed

    def add_operation(self):
        """Add an operation to the stack of operations."""
        self.py_lines.append("stack.append(x)")
        self.operators.append(self.ti_instruction["type"])

    def add_py_code_to_main_function(self, py_code):
        """Add the Python code translated from the TI instructions to the main function."""
        with open(current_app.root_path + "/models/calculator.py", "r") as file:
            calculator = file.read()
        # Revert possible formatter erronous fix
        calculator = calculator.replace("label.label_rst", "label .label_rst")
        replacement = "label .label_rst\n    " + py_code
        py_code = calculator.replace("label .label_rst", replacement, 1)
        return py_code

    def change_program_stop_to_return_in_main(self, py_lines):
        """Change program stops in the main function to simple return statements instead of raising an exception."""
        original = py_lines.copy()
        changed_program_stop = False
        for number, py_line in enumerate(py_lines):
            if py_line.startswith("def"):
                # This is a new function definition, main has been processed
                break
            if "label .label_" in py_line and changed_program_stop:
                # A program stop was changed before a label which the with_goto decorator cannot handle
                # Restore the original lines of code
                py_lines = original.copy()
                break
            if "# R/S" in py_line:
                # This is a line starting with "raise UserWarning('R/S') # R/S"
                key = "R/S"
                ti_instruction = instruction_set[key]
                ti_instruction.update(value=key)
                py_lines[number] = self.format_py_line("return", ti_instruction)
                changed_program_stop = True
        return py_lines

    def extract_description(self, ti_instructions):
        """Extract the description at the begining of the program."""
        description = ""
        input_data_pieces = ti_instructions.split("# Data", 1)

        if len(input_data_pieces) != 1:
            # This is a Data Input/Processing section, assuming this is a description above
            description, ti_instructions = input_data_pieces
            ti_instructions = "# Data" + ti_instructions

            if description and re.search(
                r"^ *[^#].*?$", re.sub(r"\n+", r"\n", description), re.M
            ):
                # There is an instruction inside the description, assuming this is not a description
                ti_instructions = description + ti_instructions
                description = ""

        return [ti_instructions, description]

    def extract_last_comments(self, py_lines):
        """Extract the comments of a subroutine."""
        comments = []
        for py_line in reversed(py_lines):
            if py_line and py_line[0] != "#":
                break
            comments.insert(0, py_line)
            py_lines.pop()
        return comments

    def extract_subroutine_numbers(self, py_lines):
        """Extract subroutine numbers."""
        subroutine_numbers = []
        for py_line in py_lines:
            subroutine_number = self.get_subroutine_number(py_line)
            if subroutine_number:
                subroutine_numbers.append(subroutine_number)
        return subroutine_numbers

    def fix_newlines(self, ti_instructions):
        return re.sub(r"(\r\n|\r)", r"\n", ti_instructions)

    def format_py_line(self, py_line, ti_instruction):
        """Format a Python line, format = Python # TI instruction (TI code)."""
        fixed = f"{py_line: <{self.PY_LINE_LENGTH}} # {ti_instruction['value']: <{self.TI_INSTRUCTION_LENGTH}}"
        if "ti_code" in ti_instruction:
            fixed += f" ({ti_instruction['ti_code'].strip()})"
        return fixed

    def generate_py_code(self, ti_instructions):
        """Generate the Python code from the TI instructions (the class entry point)."""
        ti_instructions = self.fix_newlines(ti_instructions)
        ti_instructions, description = self.extract_description(ti_instructions)
        py_lines = self.translate_ti_instructions_to_py_lines(
            ti_instructions, description
        )
        self.indent_if_statement(py_lines)

        subroutine_numbers = self.extract_subroutine_numbers(py_lines)
        if subroutine_numbers:
            py_lines = self.add_functions(py_lines, subroutine_numbers)
            self.add_end_labels(py_lines)
        py_lines = self.change_program_stop_to_return_in_main(py_lines)

        self.indent_lines(py_lines)
        py_code = "\n".join(py_lines)
        py_code = self.remove_extra_lines(py_code)
        py_code = py_code.lstrip()

        py_code = self.add_py_code_to_main_function(py_code)
        py_code = description + py_code
        py_code = py_code.strip()

        return py_code

    def get_label_number(self, py_line):
        """Extract label numbers to be matched against subroutine calls."""
        match = re.match(r"label .label_(\d)", py_line)
        if match:
            return match.group(1)

    def get_subroutine_number(self, py_line):
        """Extract the subroutine number."""
        match = re.search(r"sbr_(\d)", py_line)
        if match:
            return match.group(1)

    def indent_lines(self, py_lines):
        """Indent the Python lines of code."""
        preceedes_def = False
        last = len(py_lines) - 1
        for number, py_line in enumerate(reversed(py_lines)):
            if not py_line:
                # This is a blank line, typically preceeding a function definition
                preceedes_def = False
            elif py_line[0:3] == "def":
                # This is a function definition
                preceedes_def = True
            elif not preceedes_def and py_line != "\n":
                # This is any line of code
                py_lines[last - number] = "    " + py_line.rstrip()
            # Else this is a comment or the "with_goto" decorator preceeding the function definition

    def indent_if_statement(self, py_lines):
        """Ident the Python code following an if statement."""
        follows_if_statement = False
        for number, py_line in enumerate(py_lines):
            if not py_line:
                # Ignore empty py_lines
                continue
            if follows_if_statement:
                # This is a line following an "if" statement
                if self.is_if_statement(py_line):
                    raise Exception(
                        'Translation error: nested "if" statements not allowed: {py_line}'
                    )
                # Ident the line and move the instruction part to the left
                py_lines[number] = "    " + py_line.replace("    #", "#", 1)
                if py_line[0] != "#":
                    # This is the line of code, the end of the "if" statement
                    follows_if_statement = False
                # Else this is a comment line and not yet the py_line of code following the "if" statement
            elif self.is_if_statement(py_line):
                follows_if_statement = True

    def is_if_statement(self, py_line):
        """Test if the line of code is an if statement."""
        return py_line and (py_line[0:2] == "if" or py_line[0:4] == "elif")

    def process_prev_equality(self):
        """Process the multiplication stacked before an addition."""
        self.process_prev_multiplication()
        if self.prev_operator == "+" or self.prev_operator == "-":
            self.operators.pop()
            self.py_lines.append("y = stack.pop()")
            self.py_lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_multiplication(self):
        """Process the power operation stacked before a multiplication."""
        self.process_prev_power()
        if self.prev_operator == "*" or self.prev_operator == "/":
            self.operators.pop()
            self.py_lines.append("y = stack.pop()")
            self.py_lines.append(f"x = y {self.prev_operator} x")
            self.update_prev_operator()

    def process_prev_power(self):
        """Process the scientific notation number before a power operator."""
        self.process_prev_scientific_notation()
        if self.prev_operator == "power" or self.prev_operator == "root":
            self.operators.pop()
            self.py_lines.append("y = stack.pop()")
            exponent_sign = "-" if self.prev_operator == "root" else ""
            self.py_lines.append(f"x = pow(y, {exponent_sign}x)")
            self.update_prev_operator()

    def process_prev_scientific_notation(self):
        """Process the numbers around the EE operator."""
        self.update_prev_operator() if self.operators else None
        if self.prev_operator == "EE":
            self.operators.pop()
            self.py_lines.append("y = stack.pop()")
            self.py_lines.append("x = y * pow(10, x)")
            self.update_prev_operator()

    def remove_extra_lines(self, py_code):
        """Remove extra blank lines (2 following blank lines max)."""
        return re.sub(r"\n{2,}", r"\n\n", py_code)

    def translate_ti_instructions_to_py_lines(self, ti_instructions, description):
        """Translate the TI instructions into Python."""
        parser = Parser(ti_instructions, description, instruction_set)
        for self.ti_instruction in parser.next_instruction():
            number = len(self.py_lines)
            if self.ti_instruction["action"]:
                action = getattr(self, "action_" + self.ti_instruction["action"])
                action()
            if len(self.py_lines) == number:  # No python line added, ex. "INV SBR"
                self.py_lines.append("")
            if self.ti_instruction["action"] != "comment":
                self.py_lines[number] = self.format_py_line(
                    self.py_lines[number], self.ti_instruction
                )

        return self.py_lines

    def update_prev_operator(self):
        self.prev_operator = self.operators[-1] if self.operators else None
