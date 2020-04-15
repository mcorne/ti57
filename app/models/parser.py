import re

from tokens import tokens


class Parser:
    DECIMAL = r"(\d*\.\d+)|(\d+\.\d*)"
    INTEGER = r"\d+"

    def __init__(self, code):
        self.lower_case_tokens = self.get_lower_case_tokens(tokens)
        self.token_patterns = self.get_token_patterns(tokens)
        self.tokens = tokens
        self.step = 0
        self.parsed_tokens = self.parse(code)

    def get_lower_case_tokens(self, tokens):
        return dict([(token.lower(), token) for token in tokens.keys()])

    def get_next_token(self):
        try:
            token = self.parsed_tokens[self.step]
        except IndexError:
            return

        if Parser.is_numeric(token):
            token_details = {"action": "numeric"}
        else:
            lower_case_token = token.lower()

            if not lower_case_token in self.lower_case_tokens:
                raise Exception("Invalid token: " + token)

            token_details = self.tokens[self.lower_case_tokens[lower_case_token]]

            if not "action" in token_details:
                raise Exception("Token action not implemented: " + token)

        token_details["step"] = self.step
        token_details["token"] = token

        self.step += 1

        return token_details

    def get_token_patterns(self, tokens):
        patterns = []
        for token in tokens.keys():
            # Escape metacharacters within tokens
            # See https://docs.python.org/3/howto/regex.html#regex-howto
            # Cannot use re.escape() that escapes spaces and other characters depending on Python version!
            token = re.sub(r"[.\^$*+?{}[\]|()]", r"\\\g<0>", token)
            # Allow duplicate spaces within tokens
            token = token.replace(" ", " +")
            patterns.append(token)

        # Adds decimals, integers then anything else that is space separated
        patterns += [Parser.DECIMAL, Parser.INTEGER, r"\S+"]
        return "(" + "|".join(patterns) + ")"

    @classmethod
    def is_numeric(cls, token):
        return re.fullmatch("({}|{})".format(cls.DECIMAL, cls.INTEGER), token)

    def parse(self, code):
        return [token[0] for token in re.findall(self.token_patterns, code, re.I)]


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
p = Parser(code)
print(p.parsed_tokens)
print(p.get_next_token())
print(p.get_next_token())
print(p.get_next_token())
