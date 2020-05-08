import re


class Parser:
    DECIMAL = r"([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)"
    INTEGER = r"[0-9]+"
    # https://docs.python.org/3/howto/regex.html#regex-howto
    METACHARACTERS = r"[.\^$*+?{}[\]|()]"
    MISMATCH = r"\S+"

    def __init__(self, ti_instructions, ti_instruction_set, description_line_count):
        self.description_line_count = description_line_count
        self.ti_instructions = ti_instructions  # expecting \n line ending
        self.ti_instruction_set = ti_instruction_set

    def convert_key_to_pattern(self, key):
        # Escape metacharacters
        # Cannot use re.escape() that escapes spaces etc. depending on Python version!
        pattern = re.sub(Parser.METACHARACTERS, r"\\\g<0>", key)
        # Allow duplicate spaces
        pattern = pattern.replace(" ", " +")
        if "NUMBER" in pattern:
            # This is an instruction with an instance number, ex. "STO NUMBER" for "STO 7" etc.
            # Create a pattern to capture the instance number with a group name based on the original key
            # and a prefix so it can be found easily in the group dictionary, ex. "_KEY_STO_NUMBER".
            pattern = pattern.replace(
                "NUMBER", f"(?P<_KEY_{key.replace(' ', '_')}>[0-9])"
            )
        return pattern

    def fix_number_in_py_lines(self, number, py_lines):
        if type(py_lines) is not list:
            py_lines = [py_lines]
        py_lines = [py_line.replace("NUMBER", number) for py_line in py_lines]
        return py_lines

    def get_original_key_and_number(self, groups):
        group_name, number = next(
            (
                [group_name, number]
                for group_name, number in groups.items()
                if "_KEY_" in group_name and number is not None
            ),
            [None, None],
        )
        if group_name:
            original_key = group_name.replace("_KEY_", "").replace("_", " ")
        else:
            original_key = None
        return [original_key, number]

    def move_inline_comments_up(self):
        self.ti_instructions = re.sub(
            r"^(.*?[^ \n] *)(#.*?)$", r"\g<2>\n\g<1>", self.ti_instructions, 0, re.M
        )

    # See https://docs.python.org/3.8/library/re.html#writing-a-tokenizer
    def next_instruction(self):
        self.set_lower_case_keys()
        self.set_instruction_patterns()
        self.validate_instructions()
        self.move_inline_comments_up()
        return self.tokenizer()

    def process_key_type_instruction(self, ti_instruction, groups):
        original_key, number = self.get_original_key_and_number(groups)
        if original_key is not None:
            value = original_key
        else:
            value = ti_instruction["value"]

        lower_case_key = value.lower()
        if not lower_case_key in self.lower_case_keys:
            raise Exception(f"Parsing error: invalid instruction key {value}")

        ti_instruction.update(
            self.ti_instruction_set[self.lower_case_keys[lower_case_key]]
        )
        if not "action" in ti_instruction:
            raise Exception(f"Parsing error: action not implemented for {value}")

        if number is not None:
            if not "py_line" in ti_instruction:
                raise Exception(f"Parsing error: python line missing for {value}")
            ti_instruction["py_line"] = self.fix_number_in_py_lines(
                number, ti_instruction["py_line"]
            )
        return ti_instruction

    def process_token(self, match, start, line):
        column = match.start() - start
        type = match.lastgroup
        value = match.group()
        groups = match.groupdict()

        ti_instruction = {"value": value}

        if type == "COMMENT":
            ti_instruction["action"] = "comment"
        elif type == "KEY":
            ti_instruction = self.process_key_type_instruction(ti_instruction, groups)
        elif type == "MISMATCH":
            raise Exception(
                f"Syntax error: unexpected character {value} on line {line} and column {column}"
            )
        elif type == "DOUBLE_NEWLINE":
            start = match.end()
            line += len(value)
            ti_instruction["action"] = "comment"
        elif type == "NEWLINE":
            start = match.end()
            line += 1
            ti_instruction["action"] = "continue"
        elif type == "NUMERIC":
            ti_instruction["action"] = "numeric"
        elif type == "SKIP":
            ti_instruction["action"] = "continue"
        else:
            raise Exception(f"Parsing error: unexpected instruction type {type}")

        return [start, line, ti_instruction]

    def set_instruction_patterns(self):
        patterns = [
            self.convert_key_to_pattern(key) for key in self.ti_instruction_set.keys()
        ]
        groups = [
            ("KEY", "|".join(patterns)),
            ("NUMERIC", Parser.DECIMAL + "|" + Parser.INTEGER),
            ("COMMENT", r"#[^\n]*"),
            ("DOUBLE_NEWLINE", r"\n{2,}"),
            ("NEWLINE", r"\n"),
            ("SKIP", r"[ \t]+"),
            ("MISMATCH", r"."),
        ]
        self.patterns = "|".join("(?P<%s>%s)" % group for group in groups)

    def set_lower_case_keys(self):
        self.lower_case_keys = dict(
            [(key.lower(), key) for key in self.ti_instruction_set.keys()]
        )

    # See https://docs.python.org/3.8/library/re.html#writing-a-tokenizer
    def tokenizer(self):
        line = self.description_line_count
        start = 0
        for match in re.finditer(self.patterns, self.ti_instructions, re.I):
            start, line, ti_instruction = self.process_token(match, start, line)
            if ti_instruction["action"] != "continue":
                yield ti_instruction

    def validate_instructions(self):
        line = self.description_line_count
        start = 0
        for match in re.finditer(self.patterns, self.ti_instructions, re.I):
            start, line, dummy = self.process_token(match, start, line)
