import array
import sys
import ROOT

input_filename = "data_text/mmt_hit_print_h0.0009_ctx2_ctuv1_uverr0.0035_setxxuvuvxx_ql1_qdlm1_qbg0_qt0_NOM_NOMPt100GeV.digi.ntuple.txt"
lines = open(input_filename).readlines()

output_filename = "data_root/ntuple_sw.root"
outfile         = ROOT.TFile.Open(output_filename, "recreate")
tree            = ROOT.TTree("physics", "physics")
branches        = {}

planes = {}
planes["x"] = [0, 1, 6, 7]
planes["u"] = [2, 4]
planes["v"] = [3, 5]

floats = ["true_theta", "true_phi", "true_dtheta",
          "mx", "my", "mxl", "theta", "phi", "dtheta",
          "mxg", "mug", "mvg",
          "hit_n", "event"]
vectors = ["hit_time", "hit_vmm", "hit_plane", "hit_station",
           "hit_strip", "hit_slope", "hit_bcid"]

def main():

    initialize_branches()

    print 
    print "input:  %10i events :: %s" % (len(filter(lambda line: "%Ev" in line, lines)), input_filename)

    pitch      = 0.445
    bcid       = 20
    bcid_delta = 5

    ybases_0 = bases(lines, "Y", position=0)
    ybases_1 = bases(lines, "Y", position=1)
    zbases_0 = bases(lines, "Z", position=0)

    for index, line in enumerate(lines):

        line = line.strip()

        # delimiter of a new event
        if not line.startswith("%Ev"):
            continue

        nlines = 0
        has_summary = True
        while True:
            nlines += 1
            if "%Ev" in lines[index + nlines]:
                has_summary = False
                break
            if lines[index + nlines].startswith("---"):
                nlines += 1
                break

        if has_summary:
            event_lines = lines[index : index+nlines]
            event_lines = [li.strip() for li in event_lines]
            write_to_tree(event_lines, bcid)

        bcid += bcid_delta

    print "output: %10i events :: %s" % (tree.GetEntries(), output_filename)
    print 

    tree.GetCurrentFile().Write()
    tree.GetCurrentFile().Close()

def write_to_tree(event_lines, bcid):

    if len(event_lines) < 2:
        fatal("All events should have at least two lines!\n %s" % event_lines)

    header = event_lines[0]
    hits   = event_lines[1: -1]
    footer = event_lines[-1]

    header_firstword = header.split()[0]
    event = header_firstword.replace("%Ev", "")
    branches["event"][0] = float(event)

    slopes = {}
    slopes["x"] = []
    slopes["u"] = []
    slopes["v"] = []

    for line in hits:
        line = ", ".join(line.split())
        time, vmm, plane, station, strip, slope = eval(line)
        hit_bcid = int(time - 50) / 25 # ie, 60 => 0, 80 => 1, 110 => 2
        branches["hit_time"   ].push_back(time)
        branches["hit_vmm"    ].push_back(vmm)
        branches["hit_plane"  ].push_back(plane)
        branches["hit_station"].push_back(station)
        branches["hit_strip"  ].push_back(strip)
        branches["hit_slope"  ].push_back(slope)
        branches["hit_bcid"   ].push_back(bcid + hit_bcid)
        for pl in ["x", "u", "v"]:
            if plane in planes[pl]: 
                slopes[pl].append(slope)

    footer = footer.strip("-")
    footer = footer.split("=")[-1]
    true_theta, true_phi, true_dtheta, mx, my, mxl, theta, phi, dtheta = eval(footer)

    branches["true_theta" ][0] = true_theta
    branches["true_phi"   ][0] = true_phi
    branches["true_dtheta"][0] = true_dtheta
    branches["mx"         ][0] = mx
    branches["my"         ][0] = my
    branches["mxl"        ][0] = mxl
    branches["mxg"        ][0] = average(slopes["x"])
    branches["mug"        ][0] = average(slopes["u"])
    branches["mvg"        ][0] = average(slopes["v"])
    branches["theta"      ][0] = theta
    branches["phi"        ][0] = phi
    branches["dtheta"     ][0] = dtheta
    branches["hit_n"      ][0] = len(hits)

    tree.Fill()
    reset_branches()

def initialize_branches():
    for var in floats:
        branches[var] = array.array("f", [0.0])
        tree.Branch(var, branches[var], "%s/%s" % (var, "F"))
    for var in vectors:
        branches[var] = ROOT.vector("float")()
        branches[var].clear()
        tree.Branch(var, branches[var])

def reset_branches():
    for var in floats:
        branches[var][0] = 0
    for var in vectors:
        branches[var].clear()

def bases(lines, coord, position):
    if coord not in ["Y", "Z"]:                                   fatal("Bad coordinate for bases: %s"  % coord)
    if coord == "Y" and not position in [0, 1]:                   fatal("Bad position for bases: %s %s" % (coord, position))
    if coord == "Z" and not position in [0, 1, 2, 3, 4, 5, 6, 7]: fatal("Bad position for bases: %s %s" % (coord, position))
        
    for index, line in enumerate(lines):
        if coord+" BASES" in line:
            bases_line = lines[index + position + 1]
            return bases_line.strip().split()

def average(li):
    if not li: 
        return 0
    return sum(li) / float(len(li))

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
