# The instruction set is actually a dictionary within a formatted string that will be evaluated before use.
# Using a string prevents accidental reformatting by the formatter of the source code editor.
instruction_set = """
{
"lnx"              : {"ti_code": "  13"  , "action": "python"                , "python": "x = math.log(x)"},
"INV lnx"          : {"ti_code": "- 13"  , "action": "python"                , "python": "x = math.exp(x)"},
"CE"               : {"ti_code": "  14"  , "action": "python"                , "python": "x = 0"},
"CLR"              : {"ti_code": "  15"  , "action": "clear"},
"2nd log"          : {"ti_code": "  18"  , "action": "python"                , "python": "x = math.log10(x)"},
"INV 2nd log"      : {"ti_code": "- 18"  , "action": "python"                , "python": "x = math.pow(x, 10)"},
"2nd Ct"           : {"ti_code": "  19"  , "action": "python"                , "python": "sto[7] = 0"},
"INV 2nd Ct"       : {"ti_code": "- 19"  , "action": "clear_all"},
"2nd tan"          : {"ti_code": "  20"  , "action": "python"                , "python": "x = math.tan(unit2rad(x))"},
"INV 2nd tan"      : {"ti_code": "- 20"  , "action": "python"                , "python": "x = rad2unit(math.atan(x))"},
"x<>t"             : {"ti_code": "  22"  , "action": "python"                , "python": [
                                                                                    "y = sto[7]",
                                                                                    "sto[7] = x",
                                                                                    "x = y",
                                                                                ]},
"x2"               : {"ti_code": "  23"  , "action": "python"                , "python": "x *= x"},
"V2"               : {"ti_code": "  24"  , "action": "python"                , "python": "x = math.sqrt(x)"},
"1/x"              : {"ti_code": "  25"  , "action": "python"                , "python": "x = 1 / x"},
"2nd D.MS"         : {"ti_code": "  26"  , "action": "python"                , "python": "x = dms2degrees(x)"},
"INV 2nd D.MS"     : {"ti_code": "- 26"  , "action": "python"                , "python": "x = degrees2dms(x)"},
"2nd P->R"         : {"ti_code": "  27"  , "action": "python"                , "python": [
                                                                                    "t = x",
                                                                                    "y = unit2rad(t)",
                                                                                    "x = sto[7] * math.sin(y)",
                                                                                    "sto[7] = sto[7] * math.cos(y)",
                                                                                ]},
"INV 2nd P->R"     : {"ti_code": "- 27"  , "action": "python"                , "python": [
                                                                                    "y = x",
                                                                                    "x = rad2unit(math.atan2(y, sto[7]))",
                                                                                    "sto[7] = math.sqrt(sto[7] * sto[7] + y * y)",
                                                                                ]},
"2nd sin"          : {"ti_code": "  28"  , "action": "python"                , "python": "x = math.sin(unit2rad(x))"},
"INV 2nd sin"      : {"ti_code": "- 28"  , "action": "python"                , "python": "x = rad2unit(math.asin(x))"},
"2nd cos"          : {"ti_code": "  29"  , "action": "python"                , "python": "x = math.cos(unit2rad(x))"},
"INV 2nd cos"      : {"ti_code": "- 29"  , "action": "python"                , "python": "x = rad2unit(math.acos(x))"},
"2nd pi"           : {"ti_code": "  30"  , "action": "python"                , "python": "x = math.pi"},
"STO NUMBER"       : {"ti_code": "  32 0", "action": "python"                , "python": "sto[NUMBER] = x"},
"RCL NUMBER"       : {"ti_code": "  33 0", "action": "python"                , "python": "x = sto[NUMBER]"},
"SUM NUMBER"       : {"ti_code": "  34 0", "action": "python"                , "python": "sto[NUMBER] += x"},
"INV SUM NUMBER"   : {"ti_code": "- 34 0", "action": "python"                , "python": "sto[NUMBER] -= x"},
"y^x"              : {"ti_code": "  35"  , "action": "power"                 , "type": "power"},
"INV y^x"          : {"ti_code": "- 35"  , "action": "power"                 , "type": "root"},
"2nd Pause"        : {"ti_code": "  36"  , "action": "python"                , "python": "time.sleep(1)"},
"2nd Exc NUMBER"   : {"ti_code": "  38 7", "action": "python"                , "python": [
                                                                                    "y = sto[NUMBER]",
                                                                                    "sto[NUMBER] = x",
                                                                                    "x = y",
                                                                                ]},
"2nd Prod NUMBER"  : {"ti_code": "  39 0", "action": "python"                , "python": "sto[NUMBER] *= x"},
"INV 2nd Prod NUMBER": {"ti_code": "- 39 0", "action": "python"              , "python": "sto[NUMBER] /= x"},
"2nd |x|"          : {"ti_code": "  40"  , "action": "python"                , "python": "x = math.abs(x)"},
"EE"               : {"ti_code": "  42"  , "action": "scientific_notation"   , "type": "EE"},
"INV EE"           : {"ti_code": "- 42"  , "action": "python"                , "python": "ee = True"},
"("                : {"ti_code": "  43"  , "action": "open_parenthesis"      , "type": "("},
")"                : {"ti_code": "  44"  , "action": "closing_parenthesis"   , "type": ")"},
"2nd Nop"          : {"ti_code": "  46"  , "action": "python"                , "python": ""},
"2nd Fix"          : {"ti_code": "  48"  , "action": "python"                , "python": "rounding = x"},
"INV 2nd Fix"      : {"ti_code": "- 48"  , "action": "python"                , "python": "rounding = None"},
"2nd Int"          : {"ti_code": "  49"  , "action": "python"                , "python": "x = int(x)"},
"INV 2nd Int"      : {"ti_code": "- 49"  , "action": "python"                , "python": "x = x - int(x)"},
"2nd Deg"          : {"ti_code": "  50"  , "action": "python"                , "python": "unit = 'Deg'"},
"GTO NUMBER"       : {"ti_code": "  51 0", "action": "python"                , "python": "goto .label_NUMBER"},
"2nd Dsz"          : {"ti_code": "  56"  , "action": "python"                , "python": [
                                                                                    "sto[0] = math.floor(sto[0])",
                                                                                    "if sto[0] > 0:",
                                                                                    "sto[0] -= 1",
                                                                                    "elif sto[0] < 0:",
                                                                                    "sto[0] += 1",
                                                                                    "if sto[0] != 0:",
                                                                                ]},
"INV 2nd Dsz"      : {"ti_code": "- 56"  , "action": "python"                , "python": [
                                                                                    "sto[0] = math.floor(sto[0])",
                                                                                    "if sto[0] > 0:",
                                                                                    "sto[0] -= 1",
                                                                                    "elif sto[0] < 0:",
                                                                                    "sto[0] += 1",
                                                                                    "if sto[0] == 0:",
                                                                                ]},
"2nd Rad"          : {"ti_code": "  60"  , "action": "python"                , "python": "unit = 'Rad'"},
"SBR NUMBER"       : {"ti_code": "  61 0", "action": "python"                , "python": "sbr_NUMBER()"},
"INV SBR"          : {"ti_code": "- 61"  , "action": None,},
"2nd x=t"          : {"ti_code": "  66"  , "action": "python"                , "python": "if x == sto[7]:"},
"INV 2nd x=t"      : {"ti_code": "- 66"  , "action": "python"                , "python": "if x != sto[7]:"},
"2nd Grd"          : {"ti_code": "  70"  , "action": "python"                , "python": "unit = 'Grd'"},
"RST"              : {"ti_code": "  71"  , "action": "python"                , "python": "goto .label_rst"},
"2nd x>=t"         : {"ti_code": "  76"  , "action": "python"                , "python": "if x >= sto[7]:"},
"INV 2nd x>=t"     : {"ti_code": "- 76"  , "action": "python"                , "python": "if x < sto[7]:"},
"2nd s2"           : {"ti_code": "  80"  , "action": "python"                , "python": "x = (sto[2] - sto[1] * sto[1] / sto[0]) / sto[0]"}, # var(Y) = sum(Y^2) / N - avg(Y)
"INV 2nd s2"       : {"ti_code": "- 80"  , "action": "python"                , "python": "x = (sto[4] - sto[3] * sto[3] / sto[0]) / sto[0]"}, # var(X) = sum(X^2) / N - avg(X)
"R/S"              : {"ti_code": "  81"  , "action": "python"                , "python": "raise UserWarning('R/S')"},
"+/-"              : {"ti_code": "  84"  , "action": "python"                , "python": "x = -x"},
"="                : {"ti_code": "  85"  , "action": "equality"              , "type": "="},
"2nd Lbl NUMBER"   : {"ti_code": "  86 0", "action": "python"                , "python": "label .label_NUMBER"},
"2nd S+"           : {"ti_code": "  88"  , "action": "python"                , "python": [
                                                                                    "sto[0] += 1",  # population
                                                                                    "sto[1] += x",  # sum Y
                                                                                    "sto[2] += x * x",  # sum Y * Y
                                                                                    "sto[3] += sto[7]",  # sum X
                                                                                    "sto[4] += sto[7] * sto[7]",  # sum X * X
                                                                                    "sto[5] += sto[7] * x",  # sum X * Y
                                                                                    "sto[7] += 1",
                                                                                ]},
"INV 2nd S+"       : {"ti_code": "- 88"  , "action": "python"                , "python": [
                                                                                    "sto[0] -= 1",  # population
                                                                                    "sto[1] -= x",  # sum Y
                                                                                    "sto[2] -= x * x",  # sum Y * Y
                                                                                    "sto[3] -= sto[7]",  # sum X
                                                                                    "sto[4] -= sto[7] * sto[7]",  # sum X * X
                                                                                    "sto[5] -= sto[7] * x",  # sum X * Y
                                                                                    "sto[7] -= 1",
                                                                                ]},
"2nd x"            : {"ti_code": "  89"  , "action": "python"                , "python": "x = sto[1] / sto[0]"}, # avg(Y) = sum(Y) / N
"INV 2nd x"        : {"ti_code": "- 89"  , "action": "python"                , "python": "x = sto[3] / sto[0]"}, # avg(X) = sum(X) / N

# Operators must be after the other instructions because some of them use them, ex. "+/-"
"*"                : {"ti_code": "  55"  , "action": "multiplication"        , "type": "*"},
"+"                : {"ti_code": "  75"  , "action": "addition"              , "type": "+"},
"-"                : {"ti_code": "  65"  , "action": "addition"              , "type": "-"},
"/"                : {"ti_code": "  45"  , "action": "multiplication"        , "type": "/"},

#"."               : {"ti_code": "  83"}, # Not to be captured as a single character
}
"""
