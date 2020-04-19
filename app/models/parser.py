import re


class Parser:
    DECIMAL = r"([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)"
    INTEGER = r"[0-9]+"
    # https://docs.python.org/3/howto/regex.html#regex-howto
    METACHARACTERS = r"[.\^$*+?{}[\]|()]"
    MISMATCH = r"\S+"

    def __init__(self, instructions, instruction_set):
        self.instructions = instructions
        self.instruction_set = eval(instruction_set)

    def convert_key_to_pattern(self, key):
        # Escape metacharacters
        # Cannot use re.escape() that escapes spaces etc. depending on Python version!
        pattern = re.sub(Parser.METACHARACTERS, r"\\\g<0>", key)
        # Allow duplicate spaces
        pattern = pattern.replace(" ", " +")
        return pattern

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

    def get_lower_case_keys(self, instruction_set):
        return dict([(key.lower(), key) for key in instruction_set.keys()])

    # See https://docs.python.org/3.8/library/re.html#writing-a-tokenizer
    def next_instruction(self):
        lower_case_keys = self.get_lower_case_keys(self.instruction_set)
        patterns = self.get_instruction_patterns(self.instruction_set)
        line = 1
        start = 0
        step = 1

        for match in re.finditer(patterns, self.instructions, re.I):
            column = match.start() - start
            type = match.lastgroup
            value = match.group()

            if type == "MISMATCH":
                raise Exception(
                    f"{value} unexpected on line {line} and column {column}"
                )
            if type == "NEWLINE":
                start = match.end()
                line += 1
                continue
            if type == "SKIP":
                continue

            instruction = {"line": line, "step": step, "value": value}

            if type == "COMMENT":
                instruction["action"] = "comment"
            elif type == "NUMERIC":
                instruction["action"] = "numeric"
            elif type == "KEY":
                lower_case_key = value.lower()
                if not lower_case_key in lower_case_keys:
                    raise Exception(f"Invalid instruction key {value}")
                details = self.instruction_set[lower_case_keys[lower_case_key]]
                if not "action" in details:
                    raise Exception(f"Action not implemented for {value}")
                instruction.update(details)
            else:
                raise Exception(f"Unexpected instruction type {type}")

            step += 1
            yield instruction
