# The instruction set is actually a dictionary within a formatted string that will be evaluated before use.
# Using a string prevents accidental reformatting by the formatter of the source code editor.
instruction_set = eval(
    """
{
"lnx"              : {"ti_code": "  13"  , "action": "py_line"            , "py_line": "x = log(x)"},
"INV lnx"          : {"ti_code": "- 13"  , "action": "py_line"            , "py_line": "x = exp(x)"},
"CE"               : {"ti_code": "  14"  , "action": "py_line"            , "py_line": "x = 0"},
"CLR"              : {"ti_code": "  15"  , "action": "clear"},
"2nd log"          : {"ti_code": "  18"  , "action": "py_line"            , "py_line": "x = log10(x)"},
"INV 2nd log"      : {"ti_code": "- 18"  , "action": "py_line"            , "py_line": "x = pow(x, 10)"},
"2nd Ct"           : {"ti_code": "  19"  , "action": "py_line"            , "py_line": "mem[7] = 0"},
"INV 2nd Ct"       : {"ti_code": "- 19"  , "action": "clear_all"},
"2nd tan"          : {"ti_code": "  20"  , "action": "py_line"            , "py_line": "x = tan(unit2rad(x))"},
"INV 2nd tan"      : {"ti_code": "- 20"  , "action": "py_line"            , "py_line": "x = rad2unit(atan(x))"},
"x<>t"             : {"ti_code": "  22"  , "action": "py_line"            , "py_line": [
                                                                                "y = mem[7]",
                                                                                "mem[7] = x",
                                                                                "x = y",
                                                                            ]},
"x^2"              : {"ti_code": "  23"  , "action": "py_line"            , "py_line": "x *= x"}, # x2 (times 2) cannot be used
"V2"               : {"ti_code": "  24"  , "action": "py_line"            , "py_line": "x = sqrt(x)"},
"1/x"              : {"ti_code": "  25"  , "action": "py_line"            , "py_line": "x = 1 / x"},
"2nd D.MS"         : {"ti_code": "  26"  , "action": "py_line"            , "py_line": "x = dms2degrees(x)"},
"INV 2nd D.MS"     : {"ti_code": "- 26"  , "action": "py_line"            , "py_line": "x = degrees2dms(x)"},
"2nd P->R"         : {"ti_code": "  27"  , "action": "py_line"            , "py_line": [
                                                                                "t = x",
                                                                                "y = unit2rad(t)",
                                                                                "x = mem[7] * sin(y)",
                                                                                "mem[7] = mem[7] * cos(y)",
                                                                            ]},
"INV 2nd P->R"     : {"ti_code": "- 27"  , "action": "py_line"            , "py_line": [
                                                                                "y = x",
                                                                                "x = rad2unit(atan2(y, mem[7]))",
                                                                                "mem[7] = sqrt(mem[7] * mem[7] + y * y)",
                                                                            ]},
"2nd sin"          : {"ti_code": "  28"  , "action": "py_line"            , "py_line": "x = sin(unit2rad(x))"},
"INV 2nd sin"      : {"ti_code": "- 28"  , "action": "py_line"            , "py_line": "x = rad2unit(asin(x))"},
"2nd cos"          : {"ti_code": "  29"  , "action": "py_line"            , "py_line": "x = cos(unit2rad(x))"},
"INV 2nd cos"      : {"ti_code": "- 29"  , "action": "py_line"            , "py_line": "x = rad2unit(acos(x))"},
"2nd pi"           : {"ti_code": "  30"  , "action": "py_line"            , "py_line": "x = pi"},
"STO NUMBER"       : {"ti_code": "  32 0", "action": "py_line"            , "py_line": "mem[NUMBER] = x"},
"RCL NUMBER"       : {"ti_code": "  33 0", "action": "py_line"            , "py_line": "x = mem[NUMBER]"},
"SUM NUMBER"       : {"ti_code": "  34 0", "action": "py_line"            , "py_line": "mem[NUMBER] += x"},
"INV SUM NUMBER"   : {"ti_code": "- 34 0", "action": "py_line"            , "py_line": "mem[NUMBER] -= x"},
"y^x"              : {"ti_code": "  35"  , "action": "power"              , "type": "power"},
"INV y^x"          : {"ti_code": "- 35"  , "action": "power"              , "type": "root"},
"2nd Pause"        : {"ti_code": "  36"  , "action": "py_line"            , "py_line": "regx.append(roundn(x))"},
"2nd Exc NUMBER"   : {"ti_code": "  38 7", "action": "py_line"            , "py_line": [
                                                                                "y = mem[NUMBER]",
                                                                                "mem[NUMBER] = x",
                                                                                "x = y",
                                                                            ]},
"2nd Prod NUMBER"  : {"ti_code": "  39 0", "action": "py_line"            , "py_line": "mem[NUMBER] *= x"},
"INV 2nd Prod NUMBER": {"ti_code": "- 39 0", "action": "py_line"          , "py_line": "mem[NUMBER] /= x"},
"2nd |x|"          : {"ti_code": "  40"  , "action": "py_line"            , "py_line": "x = abs(x)"},
"EE"               : {"ti_code": "  42"  , "action": "scientific_notation", "type": "EE"},
"INV EE"           : {"ti_code": "- 42"  , "action": "py_line"            , "py_line": "ee = True"},
"("                : {"ti_code": "  43"  , "action": "opening_parenthesis", "type": "("},
")"                : {"ti_code": "  44"  , "action": "closing_parenthesis", "type": ")"},
"2nd Nop"          : {"ti_code": "  46"  , "action": "py_line"            , "py_line": ""},
"2nd Fix NUMBER"   : {"ti_code": "  48"  , "action": "py_line"            , "py_line": "rounding = NUMBER"},
"INV 2nd Fix"      : {"ti_code": "- 48"  , "action": "py_line"            , "py_line": "rounding = None"},
"2nd Int"          : {"ti_code": "  49"  , "action": "py_line"            , "py_line": "x = int(x)"},
"INV 2nd Int"      : {"ti_code": "- 49"  , "action": "py_line"            , "py_line": "x = x - int(x)"},
"2nd Deg"          : {"ti_code": "  50"  , "action": "py_line"            , "py_line": "unit = 'Deg'"},
"GTO NUMBER"       : {"ti_code": "  51 0", "action": "py_line"            , "py_line": "goto .label_NUMBER"},
"2nd Dsz"          : {"ti_code": "  56"  , "action": "py_line"            , "py_line": [
                                                                                "mem[0] = floor(mem[0])",
                                                                                "if mem[0] > 0:",
                                                                                "mem[0] -= 1",
                                                                                "elif mem[0] < 0:",
                                                                                "mem[0] += 1",
                                                                                "if mem[0] != 0:",
                                                                            ]},
"INV 2nd Dsz"      : {"ti_code": "- 56"  , "action": "py_line"            , "py_line": [
                                                                                "mem[0] = floor(mem[0])",
                                                                                "if mem[0] > 0:",
                                                                                "mem[0] -= 1",
                                                                                "elif mem[0] < 0:",
                                                                                "mem[0] += 1",
                                                                                "if mem[0] == 0:",
                                                                            ]},
"2nd Rad"          : {"ti_code": "  60"  , "action": "py_line"            , "py_line": "unit = 'Rad'"},
"SBR NUMBER"       : {"ti_code": "  61 0", "action": "py_line"            , "py_line": "sbr_NUMBER()"},
"INV SBR"          : {"ti_code": "- 61"  , "action": "py_line"            , "py_line": "return"},
"2nd x=t"          : {"ti_code": "  66"  , "action": "py_line"            , "py_line": "if x == mem[7]:"},
"INV 2nd x=t"      : {"ti_code": "- 66"  , "action": "py_line"            , "py_line": "if x != mem[7]:"},
"2nd Grad"         : {"ti_code": "  70"  , "action": "py_line"            , "py_line": "unit = 'Grd'"},
"RST"              : {"ti_code": "  71"  , "action": "py_line"            , "py_line": "goto .label_rst"},
"2nd x>=t"         : {"ti_code": "  76"  , "action": "py_line"            , "py_line": "if x >= mem[7]:"},
"INV 2nd x>=t"     : {"ti_code": "- 76"  , "action": "py_line"            , "py_line": "if x < mem[7]:"},
"2nd s2"           : {"ti_code": "  80"  , "action": "py_line"            , "py_line": "x = (mem[2] - mem[1] * mem[1] / mem[0]) / mem[0]"}, # var(Y) = sum(Y^2) / N - avg(Y)
"INV 2nd s2"       : {"ti_code": "- 80"  , "action": "py_line"            , "py_line": "x = (mem[4] - mem[3] * mem[3] / mem[0]) / mem[0]"}, # var(X) = sum(X^2) / N - avg(X)
"R/S"              : {"ti_code": "  81"  , "action": "py_line"            , "py_line": "raise UserWarning('R/S')"},
"+/-"              : {"ti_code": "  84"  , "action": "py_line"            , "py_line": "x = -x"},
"="                : {"ti_code": "  85"  , "action": "equality"           , "type": "="},
"2nd Lbl NUMBER"   : {"ti_code": "  86 0", "action": "py_line"            , "py_line": "label .label_NUMBER"},
"2nd S+"           : {"ti_code": "  88"  , "action": "py_line"            , "py_line": [
                                                                                "mem[0] += 1",  # population
                                                                                "mem[1] += x",  # sum Y
                                                                                "mem[2] += x * x",  # sum Y * Y
                                                                                "mem[3] += mem[7]",  # sum X
                                                                                "mem[4] += mem[7] * mem[7]",  # sum X * X
                                                                                "mem[5] += mem[7] * x",  # sum X * Y
                                                                                "mem[7] += 1",
                                                                            ]},
"INV 2nd S+"       : {"ti_code": "- 88"  , "action": "py_line"            , "py_line": [
                                                                                "mem[0] -= 1",  # population
                                                                                "mem[1] -= x",  # sum Y
                                                                                "mem[2] -= x * x",  # sum Y * Y
                                                                                "mem[3] -= mem[7]",  # sum X
                                                                                "mem[4] -= mem[7] * mem[7]",  # sum X * X
                                                                                "mem[5] -= mem[7] * x",  # sum X * Y
                                                                                "mem[7] -= 1",
                                                                            ]},
"2nd x"            : {"ti_code": "  89"  , "action": "py_line"            , "py_line": "x = mem[1] / mem[0]"}, # avg(Y) = sum(Y) / N
"INV 2nd x"        : {"ti_code": "- 89"  , "action": "py_line"            , "py_line": "x = mem[3] / mem[0]"}, # avg(X) = sum(X) / N

# Operators must be after the other instructions because some of them use them, ex. "+/-"
"x"                : {"ti_code": "  55"  , "action": "multiplication"     , "type": "*"},
"+"                : {"ti_code": "  75"  , "action": "addition"           , "type": "+"},
"-"                : {"ti_code": "  65"  , "action": "addition"           , "type": "-"},
"/"                : {"ti_code": "  45"  , "action": "multiplication"     , "type": "/"},

#"."               : {"ti_code": "  83"}, # Not to be captured as a single character

# Extended instructions
"*"                : {"ti_code": "  55"  , "action": "multiplication"     , "type": "*"},
}
"""
)
