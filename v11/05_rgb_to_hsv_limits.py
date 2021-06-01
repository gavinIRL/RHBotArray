import colorsys


def grab_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r/255, g/255, b/255)


hmin, hmax, smin, smax, vmin, vmax = [1, 0, 1, 0, 1, 0]

for rval in range(245, 256):
    for gval in range(195, 211):
        for bval in range(73, 84):
            h, s, v = grab_hsv(rval, gval, bval)
            if h < hmin:
                hmin = h
            if h > hmax:
                hmax = h
            if s < smin:
                smin = s
            if s > smax:
                smax = s
            if v < vmin:
                vmin = v
            if v > vmax:
                vmax = v

print("Hmin:{}, Hmax:{}".format(hmin, hmax))
print("Smin:{}, Smax:{}".format(smin, smax))
print("Vmin:{}, Vmax:{}".format(vmin, vmax))


# def print_rgb_to_hsv(r, g, b):
#     result = colorsys.rgb_to_hsv(r/255, g/255, b/255)
#     print(result)
# print("-------")
# minhealthbar = [245, 195, 73]
# r, g, b = minhealthbar
# print_rgb_to_hsv(r, g, b)
