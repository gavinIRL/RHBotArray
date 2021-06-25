import math

xdist = 61
ydist = 4
smaller = min(xdist, ydist)
diag = math.hypot(smaller, smaller)
print(diag + max(xdist, ydist) - smaller)
