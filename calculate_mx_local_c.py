"""
calculate the constants C_i for mx_local

mx_local = sum( C_i * y_i )
"""
from rootutils import int2sfi

def main():

    #              3       2       1       0
    zbases      = [7763.5, 7752.5, 7594.5, 7583.5]
    strip_pitch = 0.445
    nplanes     = len(zbases)
    nconfigs    = pow(2, nplanes)

    # word_length = 32
    # frac_length = 39

    word_length = 18
    frac_length = 25

    print
    print "-- x'WORD' -- plane config (4 bits: 3210) & plane (2 bits)."
    print "-- size of constants : %i" % (word_length)
    print "-- fixed point       : %i" % (frac_length)
    print "-- e.g. 110111 is C for the plane config 1101 and plane 11 (3)"
    print

    constants = []

    # consider each plane configuration
    for config in reversed(xrange(nconfigs)):

        configuration = format(config, "04b")

        # filter for planes with hits
        zbases_this = []
        for zbase, conf in zip(zbases, configuration):
            zbases_this.append(zbase if conf=="1" else 0)
        hit_planes = configuration.count("1")

        sum_zbasessq  = sum([base*base for base in zbases_this])
        sum_zbases_sq = pow(sum(zbases_this), 2)

        # calculate the constants A,B (these are independent of plane)
        if hit_planes > 1:
            const_A = hit_planes                 / (hit_planes*sum_zbasessq - sum_zbases_sq)
            const_B = const_A * sum(zbases_this) /  hit_planes
            zavg    =           sum(zbases_this) /  hit_planes
        else:
            const_A, const_B = 0, 0


        # consider each plane
        for plane in reversed(xrange(nplanes)):


            # skip non-triggerable configurations
            if   configuration in ["1100", "0011"] : const_C = 0
            elif hit_planes    in [0, 1]           : const_C = 0
            elif configuration[::-1][plane] == "0" : const_C = 0
            else:
                zbase = zbases[::-1][plane]
                const_C = const_B * (zbase/zavg - 1) * strip_pitch
                constants.append(const_C)


            # convert to fp
            # represent as integer, binary, and hex
            const_C_int = int(const_C * pow(2, frac_length))
            const_C_bin = int2sfi(const_C_int, word_length)
            const_C_hex = format(int(const_C_bin, base=2), "0%iX" % (word_length / 4))


            # print to screen
            if word_length%4 == 0: data = 'x"%s"' % (const_C_hex.replace("0x", ""))
            else:                  data = 'b"%s"' % (const_C_bin.replace("0b", ""))

            if const_C != 0: orig = " (%11.8f)" % (const_C)
            else:            orig = " (%11s)"   % ("unassigned")

            print "%s, -- %s%s %s" % (data, configuration, format(plane, "02b"), orig)


    # derive the appropriate fp as desired
    print "recommended fp:", recommend_fixed_point(constants, word_length)


def recommend_fixed_point(values, bits, signed=True):

    if signed:
        bits -= 1

    fp = 0
    while True:
        for val in values:
            if abs(val)*pow(2.0, fp) / pow(2.0, bits) > 1:
                return fp - 1
        else:
            fp += 1
            

if __name__ == "__main__":
    main()


