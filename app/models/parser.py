import re

from tokens import tokens


class Parser:
    DECIMAL = r"([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)"
    INTEGER = r"[0-9]+"
    # https://docs.python.org/3/howto/regex.html#regex-howto
    METACHARACTERS = r"[.\^$*+?{}[\]|()]"
    MISMATCH = r"\S+"

    def __init__(self, code):
        self.code = code
        self.lower_case_tokens = self.get_lower_case_tokens(tokens)
        self.token_patterns = self.get_token_patterns(tokens)
        self.tokens = tokens

    def convert_token_to_pattern(self, token):
        # Escape metacharacters within tokens, cannot use re.escape() that escapes too much stuff
        # including spaces plus other characters depending on Python version!
        token = re.sub(Parser.METACHARACTERS, r"\\\g<0>", token)
        # Allow duplicate spaces within tokens
        token = token.replace(" ", " +")
        return token

    def get_lower_case_tokens(self, tokens):
        return dict([(token.lower(), token) for token in tokens.keys()])

    def get_token_patterns(self, tokens):
        tokens = [self.convert_token_to_pattern(token) for token in tokens.keys()]
        groups = [
            ("TOKEN", "|".join(tokens)),
            ("NUMERIC", Parser.DECIMAL + "|" + Parser.INTEGER),
            ("NEWLINE", r"\r\n|\n|\r"),
            ("SKIP", r"[ \t]+"),
            ("MISMATCH", r"."),
        ]
        patterns = "|".join("(?P<%s>%s)" % group for group in groups)
        return patterns

    # See https://docs.python.org/3.8/library/re.html#writing-a-tokenizer
    def next_token(self):
        line = 1
        start = 0
        step = 1

        for match in re.finditer(self.token_patterns, self.code, re.I):
            column = match.start() - start
            type = match.lastgroup
            value = match.group()

            if type == "MISMATCH":
                raise RuntimeError(
                    f"{value} unexpected on line {line} and column {column}"
                )
            if type == "NEWLINE":
                start = match.end()
                line += 1
                continue
            if type == "SKIP":
                continue

            token = {"line": line, "step": step, "value": value}

            if type == "NUMERIC":
                token["action"] = "numeric"
            else:
                lower_case_token = value.lower()
                if not lower_case_token in self.lower_case_tokens:
                    raise Exception("Invalid token " + token)
                details = self.tokens[self.lower_case_tokens[lower_case_token]]
                if not "action" in details:
                    raise Exception("Action not implemented for " + token)
                token.update(details)

            step += 1
            yield token
