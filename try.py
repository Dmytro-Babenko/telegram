from datetime import date, time, datetime

d = date(2022, 3, 2)
t = time(10, 10)
a = datetime.combine(d, t)
print(a)