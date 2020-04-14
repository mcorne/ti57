import re

from tokens import tokens


class Generator:
    def __init__(self):
        self.lower_case_tokens = dict(
            [(token.lower(), token) for token in tokens.keys()]
        )
        self.tokens = tokens

    def generate_python(self, ti_code):
        token_pattern = self.set_token_pattern()
        # preg_match_all($token_pattern, $ti57_code, $matches)? $matches[1] : false
        # "~(" + "|".join(pattern) + ")~iu"
        return token_pattern

    def set_token_pattern(self):
        pattern = []
        for token in self.tokens.keys():
            token = re.escape(token)
            pattern.append(token.replace(" ", " +"))

        # captures numerics, see php.net/manual/en/language.types.float.php
        pattern.append("[0-9]*[.][0-9]+|[0-9]+[.][0-9]*")  # DNUM
        pattern.append("[0-9]+")  # LNUM
        # TODO: capture EE format, EXPONENT_DNUM (({LNUM} | {DNUM}) [eE][+-]? {LNUM}), see ti57.pdf page 2-10 !!!

        # adds pattern to captures anything else that is not spaces
        pattern.append("[^\s]+")

        return "|".join(pattern)


ti_code = """
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
python = g.generate_python(ti_code)
print(python)
