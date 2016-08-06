"""
plot_wedge :: a script for plotting quantities as they appear
              on a micromegas wedge, like theta and phi.

run like:
> python plot_wedge.py --quantity phi,theta --sector large
"""

import argparse
import math
import os

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()
import rootlogon

from trapezoid import Trapezoid
LM1, LM2 = Trapezoid("LM1"), Trapezoid("LM2")
SM1, SM2 = Trapezoid("SM1"), Trapezoid("SM2")

#
# main steering function
#
def main(quantity):

    # check user input
    if not quantity:
        fatal("Please give a --quantity to plot on the wedge")
    if not quantity in available_quantities():
        blob = "Available quantities are: \n %s" % ("\n ".join(available_quantities()))
        fatal("The script is not configured to plot %s. Would you like to add it?\n\n%s" % (quantity, blob))
    if not ops.sector.lower() in ["large", "small"]:
        fatal("Please give a --sector which is large or small")

    # the money
    xmin, xmax = -1500, 1500
    ymin, ymax =   700, 4900
    z          = (7474 + 7808) / 2.0

    nbinsx, nbinsy = 100, 200
    plane = ROOT.TH2F("plane", "", nbinsx, xmin, xmax, nbinsy, ymin, ymax)
    plane = stylize(plane, quantity)

    content = {}

    # loop across the histogram
    for xbin in xrange(plane.GetNbinsX()+1):
        for ybin in xrange(plane.GetNbinsY()+1):

            # location on the wedge
            xcenter = plane.GetXaxis().GetBinCenter(xbin)
            ycenter = plane.GetYaxis().GetBinCenter(ybin)

            # only plot stuff on the wedge
            if (ops.sector=="large" and LM1.outside_boundary(xcenter, ycenter) and LM2.outside_boundary(xcenter, ycenter)) or \
               (ops.sector=="small" and SM1.outside_boundary(xcenter, ycenter) and SM2.outside_boundary(xcenter, ycenter)):
               plane.SetBinContent(xbin, ybin, -999)
               continue

            # quantities!
            mx = xcenter / z
            my = ycenter / z
            content["mx"]               = mx
            content["my"]               = my
            content["tanphi"]           = mx / my
            content["tantheta"]         = math.sqrt(mx*mx + my*my)
            content["phi"]              = math.atan(content["tanphi"])
            content["phi_v_mx"]         = (mx - content["phi"])*1000
            content["phi_v_tanphi"]     = (content["tanphi"] - content["phi"])*1000
            content["theta"]            = math.atan(content["tantheta"])
            content["theta_v_my"]       = (my - content["theta"])*1000
            content["theta_v_tantheta"] = (content["tantheta"] - content["theta"])*1000
            content["mxg_to_tantheta"]  = math.sqrt(1 + (mx*mx)/(my*my))

            plane.SetBinContent(xbin, ybin, content[quantity])

    # add guiding text, too
    sect = ROOT.TLatex(0.20, 0.95, "%s sector" % (ops.sector))
    zpos = ROOT.TLatex(0.55, 0.95, "z = %i mm" % (z))
    for text in [sect, zpos]:
        text.SetTextSize(0.035)
        text.SetTextFont(42)
        text.SetNDC()

    # draw it
    name = "%s_%s" % (ops.sector, quantity)
    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Draw()
    plane.Draw("colzsame")
    for text in [sect, zpos]:
        text.Draw()

    # save it
    if not os.path.isdir(ops.output):
        os.makedirs(ops.output)
    filename = os.path.join(ops.output, canvas.GetName()+".pdf")
    canvas.SaveAs(filename)


def stylize(th2, quantity):

    th2.GetXaxis().SetTitle("x [mm]")
    th2.GetYaxis().SetTitle("y [mm]")
    th2.GetZaxis().SetTitle(ztitle(quantity))

    th2.GetXaxis().SetTitleOffset(1.2)
    th2.GetYaxis().SetTitleOffset(1.8)
    th2.GetZaxis().SetTitleOffset(1.8)

    ROOT.gStyle.SetPadLeftMargin  (0.18)
    ROOT.gStyle.SetPadRightMargin (0.24)
    ROOT.gStyle.SetPadTopMargin   (0.06)
    ROOT.gStyle.SetPadBottomMargin(0.13)

    ROOT.gStyle.SetNumberContours(300)
    th2.GetXaxis().SetNdivisions(505)

    zmin, zmax = zbounds(quantity)
    th2.SetMinimum(zmin)
    th2.SetMaximum(zmax)

    return th2

def ztitle(string):
    if string == "mx"               : return "m#lower[0.3]{#scale[0.7]{x}}"
    if string == "my"               : return "m#lower[0.3]{#scale[0.7]{y}}"
    if string == "tanphi"           : return "tan(#phi)"
    if string == "tantheta"         : return "tan(#theta)"
    if string == "phi"              : return "#phi"
    if string == "phi_v_mx"         : return "(%s #font[122]{-} #phi) #times 10^{3}" % (ztitle("mx"))
    if string == "phi_v_tanphi"     : return "(%s #font[122]{-} #phi) #times 10^{3}" % (ztitle("tanphi"))
    if string == "theta"            : return "#theta"
    if string == "theta_v_my"       : return "(%s #font[122]{-} #theta) #times 10^{3}" % (ztitle("my"))
    if string == "theta_v_tantheta" : return "(%s #font[122]{-} #theta) #times 10^{3}" % (ztitle("tantheta"))
    if string == "mxg_to_tantheta"  : return "#sqrt{1 + m#lower[0.3]{#scale[0.7]{x}}^{2} / m#lower[0.3]{#scale[0.7]{y}}^{2}}"


def zbounds(string):
    if string == "mx"               : return (-0.20, 0.20)
    if string == "my"               : return ( 0.05, 0.65)
    if string == "tanphi"           : return (-0.50, 0.50)
    if string == "tantheta"         : return ( 0.05, 0.65)
    if string == "phi"              : return (-0.50, 0.50)
    if string == "theta"            : return ( 0.05, 0.65)
    if string == "theta_v_my"       : return (  -20,   70)
    if string == "theta_v_tantheta" : return (  -20,   70)
    if string == "phi_v_mx"         : return ( -300,  300)
    if string == "phi_v_tanphi"     : return (  -20,   70)
    if string == "mxg_to_tantheta"  : return ( 0.98, 1.06)


def available_quantities():
    return ["mx", "my", "tanphi", "tantheta", "phi", "theta",
            "mxg_to_tantheta", "theta_v_my", "theta_v_tantheta",
            "phi_v_mx", "phi_v_tanphi",
            ]

def options():
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--sector",   default="large", help="the sector size of interest: large or small")
    parser.add_argument("--quantity", default="",      help="the quantities of interest (phi, theta, ...)")
    parser.add_argument("--output",   default="wedge", help="output directory for plots")
    return parser.parse_args()


def fatal(message):
    import sys
    sys.exit("\nError in %s: %s\n" % (__file__, message))


if __name__ == "__main__":
    ops = options()
    for quant in ops.quantity.split(","):
        main(quant)

