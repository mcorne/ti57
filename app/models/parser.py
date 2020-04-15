import re

from tokens import tokens


class Parser:
    def __init__(self):
        self.lower_case_tokens = self.get_lower_case_tokens(tokens)
        self.token_patterns = self.get_token_patterns(tokens)
        self.tokens = tokens

    def get_lower_case_tokens(self, tokens):
        return dict([(token.lower(), token) for token in tokens.keys()])

    def get_token_patterns(self, tokens):
        patterns = []
        for token in tokens.keys():
            # Escape metacharacters within tokens
            # See https://docs.python.org/3/howto/regex.html#regex-howto
            # Cannot use re.escape() that escapes spaces and other characters depending on Python version!
            token = re.sub(r"[.\^$*+?{}[\]|()]", r"\\\g<0>", token)
            # All duplicate spaces within tokens
            token = token.replace(" ", " +")
            patterns.append(token)

        # Adds decimals, integers then anything else that is space separated
        patterns += [r"(\d*\.\d+)|(\d+\.\d*)", r"\d+", r"\S+"]
        return "(" + "|".join(patterns) + ")"

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
p = Parser()
print(p.parse(code))
