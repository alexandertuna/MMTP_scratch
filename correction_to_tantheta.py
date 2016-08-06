import math
import sys
import rootlogon
import ROOT
ROOT.gROOT.SetBatch()

xmin, xmax = -1500, 1500
ymin, ymax =   700, 4900
z          = (7474 + 7808) / 2.0

sector   = "small"
# quantity = "mxg_to_tantheta"
quantity = "my"

from trapezoid import Trapezoid
LM1, LM2 = Trapezoid("LM1"), Trapezoid("LM2")
SM1, SM2 = Trapezoid("SM1"), Trapezoid("SM2")

def main():

    plane = ROOT.TH2F("plane", "", 200, xmin, xmax, 400, ymin, ymax)

    plane.GetXaxis().SetTitle("x [mm]")
    plane.GetYaxis().SetTitle("y [mm]")
    plane.GetZaxis().SetTitle(ztitle(quantity))

    plane.GetXaxis().SetTitleOffset(1.2)
    plane.GetYaxis().SetTitleOffset(1.8)
    plane.GetZaxis().SetTitleOffset(1.8)

    ROOT.gStyle.SetPadLeftMargin  (0.18)
    ROOT.gStyle.SetPadRightMargin (0.24)
    ROOT.gStyle.SetPadTopMargin   (0.06)
    ROOT.gStyle.SetPadBottomMargin(0.13)

    xbins = plane.GetNbinsX()+1
    ybins = plane.GetNbinsY()+1

    for xbin in xrange(xbins):
        for ybin in xrange(ybins):

            xcenter    = plane.GetXaxis().GetBinCenter(xbin)
            ycenter    = plane.GetYaxis().GetBinCenter(ybin)

            if (sector=="large" and LM1.outside_boundary(xcenter, ycenter) and LM2.outside_boundary(xcenter, ycenter)) or \
               (sector=="small" and SM1.outside_boundary(xcenter, ycenter) and SM2.outside_boundary(xcenter, ycenter)):
               plane.SetBinContent(xbin, ybin, -999)
               continue

            mx = xcenter / z
            my = ycenter / z

            content = 0
            if quantity == "mxg_to_tantheta": content = math.sqrt(1 + (mx*mx)/(my*my))
            if quantity == "mx"             : content = mx
            if quantity == "my"             : content = my

            plane.SetBinContent(xbin, ybin, content)

    ROOT.gStyle.SetNumberContours(300)
    plane.GetXaxis().SetNdivisions(505)

    zmin, zmax = zbounds(quantity)
    plane.SetMinimum(zmin)
    plane.SetMaximum(zmax)

    sect = ROOT.TLatex(0.20, 0.95, "%s sector" % (sector))
    zpos = ROOT.TLatex(0.55, 0.95, "z = %i mm" % (z))
    for text in [sect, zpos]:
        text.SetTextSize(0.035)
        text.SetTextFont(42)
        text.SetNDC()

    canvname = "correction_to_tantheta"
    canvas = ROOT.TCanvas(canvname, canvname, 800, 800)
    canvas.Draw()
    plane.Draw("colzsame")
    for text in [sect, zpos]:
        text.Draw()
    canvas.SaveAs(canvas.GetName()+".pdf")

def ztitle(string):
    if string == "mxg_to_tantheta": return "#sqrt{1 + m#lower[0.3]{#scale[0.7]{x}}^{2} / m#lower[0.3]{#scale[0.7]{y}}^{2}}"
    if string == "mx"             : return "m#lower[0.3]{#scale[0.7]{x}}"
    if string == "my"             : return "m#lower[0.3]{#scale[0.7]{y}}"

def zbounds(string):
    if string == "mxg_to_tantheta": return (0.98, 1.06)
    if string == "mx"             : return (-0.3, 0.3)
    if string == "my"             : return (0.05,  0.65)

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
