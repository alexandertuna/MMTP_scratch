"""
calculate the constants C_i for mx_local

mx_local = sum( C_i * y_i )
"""
from rootutils import int_to_signed

def main():

    #              3       2       1       0
    zbases      = [7763.5, 7752.5, 7594.5, 7583.5]
    strip_pitch = 0.445
    nplanes     = len(zbases)
    nconfigs    = pow(2, nplanes)

    word_length = 32
    frac_length = 39

    print
    print "-- x'WORD' -- plane config (4 bits: 3210) & plane (2 bits)."
    print "-- size of constants : %i" % (word_length)
    print "-- fixed point       : %i" % (frac_length)
    print "-- e.g. 110111 is C for the plane config 1101 and plane 11 (3)"
    print

    for config in reversed(xrange(nconfigs)):

        configuration = format(config, "04b")

        zbases_this = []
        for zbase, conf in zip(zbases, configuration):
            zbases_this.append(zbase if conf=="1" else 0)
        nplanes_this = configuration.count("1")

        sum_zbasessq  = sum([base*base for base in zbases_this])
        sum_zbases_sq = pow(sum(zbases_this), 2)
        
        if nplanes_this > 1:

            const_A = nplanes_this               / (nplanes_this*sum_zbasessq - sum_zbases_sq)
            const_B = const_A * sum(zbases_this) /  nplanes_this
            zavg    =           sum(zbases_this) /  nplanes_this

        else:
            const_A, const_B = 0, 0

        for plane in reversed(xrange(nplanes)):

            if   configuration in ["1100", "0011"] : const_C = 0
            elif nplanes_this  in [0, 1]           : const_C = 0
            elif configuration[::-1][plane] == "0" : const_C = 0
            else:
                zbase = zbases[::-1][plane]
                const_C = const_B * (zbase/zavg - 1) * strip_pitch

            const_C_int = int(const_C * pow(2, frac_length))
            const_C_bin = int_to_signed(const_C_int, word_length)
            const_C_hex = format(int(const_C_bin, base=2), "0%iX" % (word_length / 4))

            print "%4s %2s %12s %s %s" % (configuration, format(plane, "02b"), const_C_int, const_C_bin, const_C_hex)


if __name__ == "__main__":
    main()


