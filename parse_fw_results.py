"""
parse_fw.py :: a script for taking the MMTP FW output (text file)
               and converting it to a ROOT TTree for analysis.
               one trigger in the input text file corresponds to 
               one entry in the output ROOT TTree.

run like:
> python parse_fw.py --input=path/to/results_fw.txt --output=path/to/ntuple_fw.root
"""

import argparse
import array
import math
import os
import sys

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import rootutils

#
# output variables of the TTree
# nb: defined per trigger
#
floats = ["trig_bcid", 
          "trig_mxl", 
          "trig_mxg", 
          "trig_mug", 
          "trig_mvg", 
          "trig_dtheta", 
          "trig_tanphi", 
          "trig_tantheta",
          ]
stereo_angle = 1.5 * math.pi/180


#
# steering function
#
def main():

    ops = options()

    # retrieving input text file
    if not ops.input:
        fatal("Please provide an --input text file for parsing.")
    if not os.path.isfile(ops.input): 
        fatal("Could not find --input text file %s" % ops.input)
    lines = open(ops.input).readlines()
    print 
    print "input:  %10i events :: %s" % (len(lines), ops.input)

    # initializing output root file and tree
    if os.path.isfile(ops.output) and not ops.force==True:
        fatal("Output ROOT file already exists. Please use --force to overwrite it.")
    outfile         = ROOT.TFile.Open(ops.output, "recreate")
    tree            = ROOT.TTree("physics", "physics")
    branches        = {}
    initialize_branches(tree, branches)

    # for converting hex fw output to base10
    point_mxl      = pow(2.0, -14)
    point_mxg      = pow(2.0, -16)
    point_mug      = pow(2.0, -16)
    point_mvg      = pow(2.0, -16)
    point_dtheta   = pow(2.0, -13)
    point_tanphi   = pow(2.0,   0)
    point_tantheta = point_mxg

    # loop over triggers
    for index, line in enumerate(lines):

        line = line.strip()

        # convert hex words to physics
        packet = translate(line)

        # fill the output tree
        branches["trig_bcid"    ][0] = packet.bcid
        branches["trig_mxl"     ][0] = packet.mxl      * point_mxl
        branches["trig_mxg"     ][0] = packet.mxg      * point_mxg
        branches["trig_mug"     ][0] = packet.mug      * point_mug
        branches["trig_mvg"     ][0] = packet.mvg      * point_mvg
        branches["trig_dtheta"  ][0] = packet.dtheta   * point_dtheta
        branches["trig_tanphi"  ][0] = packet.tanphi   * point_tanphi
        branches["trig_tantheta"][0] = packet.tantheta * point_tantheta
        tree.Fill()

        # flush
        reset_branches(branches)

    # say goodbye
    print "output: %10i events :: %s" % (tree.GetEntries(), ops.output)
    print 

    # exit gracefully
    tree.GetCurrentFile().Write()
    tree.GetCurrentFile().Close()


#
# command line options for input and output
#
def options():
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input",  default=None,                       help="input text file from the firmware simulation")
    parser.add_argument("--output", default="data_root/ntuple_fw.root", help="output root file")
    parser.add_argument("--force",  action="store_true",                help="overwrite the output root file, as desired")
    return parser.parse_args()

#
# the translation!
# depends heavily on hdl/common/data_collector.vhd!
#
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
    # NB: dtheta is signed
    for key in packet.__dict__.keys():
        if key in ["dtheta"]:
            setattr(packet, key, rootutils.signed_to_int(getattr(packet, key), 16))
        else:
            setattr(packet, key, int(getattr(packet, key), base=16))

    if packet.mxg == 0:
        # failed fits
        packet.tanphi   = -1
        packet.tantheta = -1
    else:
        # derive theta and phi from mxg, mug, mvg
        packet.tanphi   =     (packet.mug - packet.mvg)/(2 * math.tan(stereo_angle)) * 1.0/packet.mxg
        packet.tantheta = pow((packet.mug - packet.mvg)/(2 * math.tan(stereo_angle)), 2.0) + pow(packet.mxg, 2.0)
        packet.tantheta = math.sqrt(packet.tantheta)

    return packet


#
# create branches in the output TTree
#
def initialize_branches(tree, branches):
    for var in floats:
        branches[var] = array.array("f", [0.0])
        tree.Branch(var, branches[var], "%s/%s" % (var, "F"))


#
# reset the branches
#
def reset_branches(branches):
    for var in floats:
        branches[var][0] = 0


#
# dummy class for now
#
class Packet():
    pass


#
# bail as necessary
#
def fatal(message):
    print
    sys.exit("Error in %s: %s\n" % (__file__, message))


#
# gogogo
#
if __name__ == "__main__":
    main()
