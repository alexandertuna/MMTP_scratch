import math
import sys
import rootlogon
import ROOT
ROOT.gROOT.SetBatch()

NSW_MM_LM1_InnerRadius = 923
NSW_MM_LM1_Length      = 2310
NSW_MM_LM1_outerRadius = NSW_MM_LM1_InnerRadius + NSW_MM_LM1_Length
NSW_MM_LMGap_Length    = 5 
NSW_MM_LM2_InnerRadius = NSW_MM_LM1_outerRadius + NSW_MM_LMGap_Length
NSW_MM_LM2_Length      = 1410
NSW_MM_LM2_outerRadius = NSW_MM_LM2_InnerRadius + NSW_MM_LM2_Length

NSW_MM_LM1_baseWidth = 640.0
NSW_MM_LM1_topWidth  = 2008.5
NSW_MM_LM2_baseWidth = 2022.8
NSW_MM_LM2_topWidth  = 2220.0

xmin, xmax = -1500, 1500
ymin, ymax = NSW_MM_LM1_InnerRadius, NSW_MM_LM2_outerRadius
z          = (7474 + 7808) / 2.0

def main():

    plane = ROOT.TH2F("plane", "", 200, xmin*1.05, xmax*1.05, 200, ymin*0.8, ymax*1.05)

    plane.GetXaxis().SetTitle("x [mm]")
    plane.GetYaxis().SetTitle("y [mm]")
    plane.GetZaxis().SetTitle("#sqrt{1 + m#lower[0.3]{#scale[0.7]{x}}^{2} / m#lower[0.3]{#scale[0.7]{y}}^{2}}")

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

            if outside_boundary(xcenter, ycenter): 
                continue

            mx         = xcenter / z
            my         = ycenter / z
            correction = math.sqrt(1 + (mx*mx)/(my*my))

            plane.SetBinContent(xbin, ybin, correction)

    ROOT.gStyle.SetNumberContours(300)
    plane.GetXaxis().SetNdivisions(505)
    plane.SetMinimum(0.98)
    plane.SetMaximum(1.06)

    canvname = "correction_to_tantheta"
    canvas = ROOT.TCanvas(canvname, canvname, 800, 800)
    canvas.Draw()
    plane.Draw("colzsame")
    canvas.SaveAs(canvas.GetName()+".pdf")

def outside_boundary(x, y):
    if y > ymax: return True
    if y < ymin: return True
    slope  = (ymax - ymin) / ((NSW_MM_LM2_topWidth - NSW_MM_LM1_baseWidth) / 2.0)
    offset = ymin - (slope * NSW_MM_LM1_baseWidth / 2.0)
    if x >  (y - offset) / slope: return True
    if x < -(y - offset) / slope: return True

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
