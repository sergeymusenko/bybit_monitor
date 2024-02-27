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
