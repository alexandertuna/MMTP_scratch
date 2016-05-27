zs = [7583.5, 7594.5, 7752.5, 7763.5]

strip_pitch = 0.445

configurations = [
    # 4X
    [1, 1, 1, 1],
    # 3X
    [1, 1, 1, 0],
    [1, 1, 0, 1],
    [1, 0, 1, 1],
    [0, 1, 1, 1],
    # 2X
    [1, 0, 0, 1],
    [0, 1, 1, 0],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    ]

def convert_to_strips_and_fixedpoint(inverse_distance, fp=-46):

    convert_to_strips = inverse_distance * strip_pitch
    convert_to_fp     = convert_to_strips / pow(2, fp)
    convert_to_hex    = hex(int(round(convert_to_fp)))
    convert_to_hex    = convert_to_hex.upper()[2:]
    return convert_to_hex

for config in configurations:

    these_zs = filter(lambda z: config[zs.index(z)] == 1, zs)
    z_average = sum(these_zs) / len(these_zs)

    print "x'%s' %s -- %s" % (convert_to_strips_and_fixedpoint(1/z_average), 
                              " "*10, 
                              "".join(str(x) for x in config),
                              )

