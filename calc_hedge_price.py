#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hedge - увиливать
# this is FOR LONG POSITION


######### 1 - where we will compensate

# pos1 HIGHER long
p1 = 10
s1 = 100

# pos2 LOWER short
p2 = 9
s2 = 400

# final price
# px =  (s1 * p1 - s2 * p2) / (s1 - s2)
px =  (s1 - s2) / (s1 / p1 - s2 / p2)

print(f"pos1: {s1:7.2f} at price {p1:7.2f}, {round(s1 / p1, 1)} coins")
print(f"pos2: {s2:7.2f} at price {p2:7.2f}, {round(s2 / p2, 1)} coins, that is {round(100 * (p2 - p1)/p1, 1)}% of price1")
print(f"dest price: {round(px, 2)}, that is {round(100 * (px - p1) / p1, 1)}% of price1")

# check
n1 = s1 / p1
n2 = s2 / p2
pr1 = s1 - n1 * px
pr2 = s2 - n2 * px
print(f"check: profit1={round(pr1, 2)}, profit2={round(pr2, 2)}")


######### 2 - which sum needed to compensate on know %% ???
