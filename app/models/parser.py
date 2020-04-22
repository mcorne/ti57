import re


class Parser:
    DECIMAL = r"([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)"
    INTEGER = r"[0-9]+"
    # https://docs.python.org/3/howto/regex.html#regex-howto
    METACHARACTERS = r"[.\^$*+?{}[\]|()]"
    MISMATCH = r"\S+"

    def __init__(self, ti_instructions, instruction_set):
        self.ti_instructions = ti_instructions
        self.ti_instruction_set = eval(instruction_set)

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

    def get_instruction_patterns(self, instruction_set):
        patterns = [self.convert_key_to_pattern(key) for key in instruction_set.keys()]
        groups = [
            ("KEY", "|".join(patterns)),
            ("NUMERIC", Parser.DECIMAL + "|" + Parser.INTEGER),
            ("COMMENT", r"#[^\n\r]*"),
            ("NEWLINE", r"\r\n|\n|\r"),
            ("SKIP", r"[ \t]+"),
            ("MISMATCH", r"."),
        ]
        patterns = "|".join("(?P<%s>%s)" % group for group in groups)
        return patterns

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

    def get_lower_case_keys(self, instruction_set):
        return dict([(key.lower(), key) for key in instruction_set.keys()])

    # See https://docs.python.org/3.8/library/re.html#writing-a-tokenizer
    def next_instruction(self):
        lower_case_keys = self.get_lower_case_keys(self.ti_instruction_set)
        patterns = self.get_instruction_patterns(self.ti_instruction_set)
        line = 1
        start = 0
        step = 1

        for match in re.finditer(patterns, self.ti_instructions, re.I):
            column = match.start() - start
            type = match.lastgroup
            value = match.group()
            groups = match.groupdict()

            if type == "MISMATCH":
                raise Exception(
                    f"Invalid instruction {value} on line {line} and column {column}"
                )
            if type == "NEWLINE":
                start = match.end()
                line += 1
                continue
            if type == "SKIP":
                continue

            ti_instruction = {"line": line, "step": step, "value": value}

            if type == "COMMENT":
                ti_instruction["action"] = "comment"
            elif type == "NUMERIC":
                ti_instruction["action"] = "numeric"
            elif type == "KEY":
                instruction_set = self.process_key_type_instruction(
                    ti_instruction, groups, lower_case_keys
                )
            else:
                raise Exception(f"Unexpected instruction type {type}")

            step += 1
            yield ti_instruction

    def process_key_type_instruction(self, ti_instruction, groups, lower_case_keys):
        original_key, number = self.get_original_key_and_number(groups)
        if original_key is not None:
            value = original_key
        else:
            value = ti_instruction["value"]
        lower_case_key = value.lower()
        if not lower_case_key in lower_case_keys:
            raise Exception(f"Invalid instruction key {value}")

        ti_instruction.update(self.ti_instruction_set[lower_case_keys[lower_case_key]])
        if not "action" in ti_instruction:
            raise Exception(f"Action not implemented for {value}")

        if number is not None:
            if not "py_line" in ti_instruction:
                raise Exception(f"Python line missing for {value}")
            ti_instruction["py_line"] = self.fix_number_in_py_lines(
                number, ti_instruction["py_line"]
            )
        return ti_instruction
