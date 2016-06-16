import array
import sys
import ROOT

input_filename = "data_text/results_nominal_0000_9999_2016_05_26.txt"
lines = open(input_filename).readlines()

output_filename = "data_root/ntuple_fw.root"
outfile         = ROOT.TFile.Open(output_filename, "recreate")
tree            = ROOT.TTree("physics", "physics")
branches        = {}

floats = ["trig_bcid", "trig_mxl", "trig_mxg", "trig_mug", "trig_mvg", "trig_dtheta",
          ]

def main():

    initialize_branches()

    print 
    print "input:  %10i events :: %s" % (len(lines), input_filename)

    point_mxl    = pow(2.0, -14)
    point_mxg    = pow(2.0, -16)
    point_mug    = pow(2.0,   0)
    point_mvg    = pow(2.0,   0)
    point_dtheta = pow(2.0,   0)

    for index, line in enumerate(lines):

        line   = line.strip()
        packet = translate(line)

        branches["trig_bcid"  ][0] = packet.bcid
        branches["trig_mxl"   ][0] = packet.mxl    * point_mxl
        branches["trig_mxg"   ][0] = packet.mxg    * point_mxg
        branches["trig_mug"   ][0] = packet.mug    * point_mug
        branches["trig_mvg"   ][0] = packet.mvg    * point_mvg
        branches["trig_dtheta"][0] = packet.dtheta * point_dtheta

        tree.Fill()
        reset_branches()

    print "output: %10i events :: %s" % (tree.GetEntries(), output_filename)
    print 

    tree.GetCurrentFile().Write()
    tree.GetCurrentFile().Close()

def translate(line):
    packet = Packet()
    packet.mxg    = line[ -4 :]
    packet.mug    = line[ -8 :  -4]
    packet.mvg    = line[-12 :  -8]
    packet.mxl    = line[-16 : -12]
    packet.mx_roi = line[-20 : -16]
    packet.dtheta = line[-24 : -20]
    packet.bcid   = line[0:4]
    # convert from hex string to integer
    for key in packet.__dict__.keys():
        setattr(packet, key, int(getattr(packet, key), base=16))
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
