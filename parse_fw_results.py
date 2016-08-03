import array
import math
import sys
import ROOT, rootutils

# input_filename = "data_text/results_nominal_0000_9999_2016_05_26.txt"
# input_filename = "data_text/results_nominal_0000_9999_2016_07_10.txt"
input_filename = "data_text/results_nominal_0000_9999_2016_07_18.txt"
# input_filename = "data_text/results_nominal_0000_9999_2016_07_30.txt"
lines = open(input_filename).readlines()

output_filename = "data_root/ntuple_fw.root"
outfile         = ROOT.TFile.Open(output_filename, "recreate")
tree            = ROOT.TTree("physics", "physics")
branches        = {}
stereo_angle    = 1.5 * math.pi/180

floats = ["trig_bcid", 
          "trig_mxl", 
          "trig_mxg", 
          "trig_mug", 
          "trig_mvg", 
          "trig_dtheta", 
          "trig_tanphi", 
          "trig_tantheta",
          ]

def main():

    initialize_branches()

    print 
    print "input:  %10i events :: %s" % (len(lines), input_filename)

    point_mxl      = pow(2.0, -14)
    point_mxg      = pow(2.0, -16)
    point_mug      = pow(2.0, -16)
    point_mvg      = pow(2.0, -16)
    point_dtheta   = pow(2.0, -13)
    point_tanphi   = pow(2.0,   0)
    point_tantheta = point_mxg

    for index, line in enumerate(lines):

        line   = line.strip()
        packet = translate(line)

        branches["trig_bcid"    ][0] = packet.bcid
        branches["trig_mxl"     ][0] = packet.mxl      * point_mxl
        branches["trig_mxg"     ][0] = packet.mxg      * point_mxg
        branches["trig_mug"     ][0] = packet.mug      * point_mug
        branches["trig_mvg"     ][0] = packet.mvg      * point_mvg
        branches["trig_dtheta"  ][0] = packet.dtheta   * point_dtheta
        branches["trig_tanphi"  ][0] = packet.tanphi   * point_tanphi
        branches["trig_tantheta"][0] = packet.tantheta * point_tantheta

        tree.Fill()
        reset_branches()

    print "output: %10i events :: %s" % (tree.GetEntries(), output_filename)
    print 

    tree.GetCurrentFile().Write()
    tree.GetCurrentFile().Close()

def translate(line):
    packet = Packet()
    packet.mxg      = line[ -4  :    ] # FITTER_DATA_PKT(15 downto 0)
    packet.mug      = line[ -8  :  -4] # FITTER_DATA_PKT(31 downto 16)
    packet.mvg      = line[-12  :  -8] # FITTER_DATA_PKT(47 downto 32)
    packet.mxl      = line[-16  : -12] # FITTER_DATA_PKT(63 downto 48)
    packet.mx_roi   = line[-20  : -16] # FITTER_DATA_PKT(79 downto 64)
    packet.dtheta   = line[-24  : -20] # FITTER_DATA_PKT(95 downto 80)
    packet.roi      = line[-28  : -24] # FITTER_DATA_PKT(111 downto 96)
    packet.bcid     = line[-96  : -92] # FITTER_DATA_PKT(383 downto 368)

    # convert from hex string to integer
    # NB: dtheta and tanphi are signed!
    for key in packet.__dict__.keys():
        if key in ["dtheta", "tanphi"]:
            setattr(packet, key, rootutils.signed_to_int(getattr(packet, key), 16))
        else:
            setattr(packet, key, int(getattr(packet, key), base=16))
                  
    if packet.mxg == 0:
        packet.tanphi   = -1
        packet.tantheta = -1
    else:
        packet.tanphi   =     (packet.mug - packet.mvg)/(2 * math.tan(stereo_angle)) * 1.0/packet.mxg
        packet.tantheta = pow((packet.mug - packet.mvg)/(2 * math.tan(stereo_angle)), 2.0) + pow(packet.mxg, 2.0)
        packet.tantheta = math.sqrt(packet.tantheta)

    return packet

def initialize_branches():
    for var in floats:
        branches[var] = array.array("f", [0.0])
        tree.Branch(var, branches[var], "%s/%s" % (var, "F"))

def reset_branches():
    for var in floats:
        branches[var][0] = 0

class Packet():
    pass

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
