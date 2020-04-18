
from calculator import *

x = 500                     # 500          #1  
sto[1] = x                  # STO 1        #2    32 1
x = 2                       # 2            #3  
sto[2] = x                  # STO 2        #4    32 2
x = sto[1]                  # RCL 1        #5    33 1
reg.append(x)               # *            #6    55
x = sto[2]                  # RCL 2        #7    33 2
y = reg.pop()               # =            #8    85
x = y * x

print(state())
