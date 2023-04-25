from datetime import date, time, datetime

a = {1: 2}
b = {2:1}
c = {3: 4}

dct = {**a, **b, **c}
print(dct)