naddr       = 1024
fixed_point = 11
output_name = "mxginverse.coe"
output_file = open(output_name, "w")

header = """
;******************************************************************
;********     MXG Div to Mult Block Memory .COE file      *********
;******************************************************************
; This is used to convert a Div to Mult in the ROI (phi) calc,
; For Single Port Block Memory v3.0 or later
; note: first data value is forced to 0000
memory_initialization_radix=16;
memory_initialization_vector=
"""
header = header.lstrip("\n")

output_file.write(header)

# from 0 to 2 - 2/naddr in naddr equal steps
mxg_inverses = [float(iaddr)/float(naddr)*(2.0 - 2.0/naddr) for iaddr in xrange(1, naddr+2)]

coeff_dec = [int(1.0 / mxg_inverse * pow(2.0, fixed_point)) for mxg_inverse in mxg_inverses]
coeff_dec[0] = 0

coeff_hex = ["%05X" % (value) for value in coeff_dec]

for icoe, coe in enumerate(coeff_hex):
    last_coe = (icoe+1 == len(coeff_hex))
    output_file.write(coe)
    output_file.write("," if not last_coe else ";")
    output_file.write("\n")

