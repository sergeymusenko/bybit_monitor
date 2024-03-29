#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# piramiding, avg price


# pos 1
p1 = 0.08
s1 = 300

# pos 2
p2 = 0.07
s2 = 600

# calc result avg price
n1 = s1 / p1
n2 = s2 / p2
px = (s1 + s2) / (n1 + n2)
print(f"{p1=}, {s1=}, {p2=}, {s2=} ==> px={round(px, 4)}")

'''
3S Strategy: до -20% в цене сохраняя до -10% в PnL
-------+---------+-----------+-----------+-----------+-----------+---
+ 6.67 | = 6.67  |-0.0% -4.0%|           |           |           |
+13.34 | =20.01  |           |-1.3% -7.5%|           |           |
+26.68 | =46.69  |           |           |-3.2% -9.7%|           |
+53.31 | =100.0  |           |           |           |-4.5% -9.6%|
-------+---------+-----------+-----------+-----------+-----------+---
       100         96          90          84          79.5
'''