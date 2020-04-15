class Generator:
    def __init__(self):
        self.code_line = []
        self.operators = []
        self.prev_operator = None
        self.token = {}

    def action_addition(self):
        self.process_prev_equality()
        self.add_operation()

    def action_clear(self):
        self.code_line.append("x = 0")
        self.code_line.append("ee = False")
        self.code_line.append("reg = []")

        self.operators = []
        self.prev_operator = None

    def action_clear_all(self):
        self.clear()
        self.code_line.append("sto = [0 for i in range(8)]")

    def action_closing_parenthesis(self):
        self.process_prev_equality()

        if self.prev_operator != "(":
            raise Exception("unexpected closing parenthesis")

        self.operators.pop()

    def action_decrement_skip_on_zero(self):
        self.code_line.append("sto[0] = math.floor(sto[0])")
        self.code_line.append("if sto[0] > 0:")
        self.code_line.append("    sto[0] -= 1")
        self.code_line.append("elif sto[0] < 0:")
        self.code_line.append("    sto[0] += 1")
        self.code_line.append("")
        self.code_line.append(token["statement"])

    def action_equality(self):
        self.process_prev_equality()

    def action_exchange_memory(self):
        self.code_line.append("y = sto[{}]".format(token["number"]))
        self.code_line.append("sto[{}] = x".format(token["number"]))
        self.code_line.append("x = y")

    def action_multiplication(self):
        self.process_prev_multiplication()
        self.add_operation()

    def action_numeric(self):
        self.code_line.append("x = {}".format(token["token"]))

    def action_open_parenthesis(self):
        self.code_line.append("")
        self.operators.append(token["type"])

    def action_polar_to_rectangular(self):
        self.code_line.append("t = x")
        self.code_line.append("y = unit2rad(t)")
        self.code_line.append("x = sto[7] * math.sin(y)")
        self.code_line.append("sto[7] = sto[7] * math.cos(y)")

    def action_power(self):
        self.process_prev_power()
        self.add_operation()

    def action_python_code(self):
        self.code_line.append(token["statement"])

    def action_rectangular_to_polar(self):
        self.code_line.append("y = x")
        self.code_line.append("x = rad2unit(math.atan2(y, sto[7]))")
        self.code_line.append("sto[7] = math.sqrt(sto[7] * sto[7] + y * y)")

    def action_scientific_notation(self):
        self.code_line.append("ee = True")
        self.add_operation()

    def action_sum(self):
        self.code_line.append("sto[0] += 1")  # population
        self.code_line.append("sto[1] += x")  # sum Y
        self.code_line.append("sto[2] += x * x")  # sum Y * Y
        self.code_line.append("sto[3] += sto[7]")  # sum X
        self.code_line.append("sto[4] += sto[7] * sto[7]")  # sum X * X
        self.code_line.append("sto[5] += sto[7] * x")  # sum X * Y
        self.code_line.append("sto[7] += 1")
