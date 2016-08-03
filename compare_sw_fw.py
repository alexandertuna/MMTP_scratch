import math
import sys
import rootutils,rootlogon
import ROOT
ROOT.gROOT.SetBatch()

filename_sw = "data_root/ntuple_sw.root"
filename_fw = "data_root/ntuple_fw.root"

file_sw = ROOT.TFile.Open(filename_sw)
file_fw = ROOT.TFile.Open(filename_fw)

tree_sw = file_sw.Get("physics")
tree_fw = file_fw.Get("physics")

region  = 6
station = 1
offset  = [65, 65,  73,  73,  73,  73, 65, 65] if station==1 else [68, 68, 110, 110, 110, 110, 68, 68]

def main():

    hists = {}
    hists["delta_mxl"]   = ROOT.TH1F("delta_mxl",   ";#Deltam_{X}^{local }(FW #font[122]{-} SW);Events", 100, -0.01, 0.01)
    hists["delta_mxg"]   = ROOT.TH1F("delta_mxg",   ";#Deltam_{X}^{global}(FW #font[122]{-} SW);Events", 100, -0.01, 0.01)
    hists["delta_mug"]   = ROOT.TH1F("delta_mug",   ";#Deltam_{U}^{global}(FW #font[122]{-} SW);Events", 100, -0.01, 0.01)
    hists["delta_mvg"]   = ROOT.TH1F("delta_mvg",   ";#Deltam_{V}^{global}(FW #font[122]{-} SW);Events", 100, -0.01, 0.01)
    hists["delta_dth"]   = ROOT.TH1F("delta_dth",   ";#Delta(#Delta#theta)(FW #font[122]{-} SW);Events", 100, -0.01, 0.01)
    hists["delta_phi"]   = ROOT.TH1F("delta_phi",   ";#Delta#phi(FW #font[122]{-} SW);Events",           100, -0.01, 0.01)
    hists["delta_theta"] = ROOT.TH1F("delta_theta", ";#Delta#theta(FW #font[122]{-} SW);Events",         100, -0.01, 0.01)

    fw, sw, diff = {}, {}, {}

    for hist in hists.values():
        hist.Sumw2()
        hist.GetXaxis().SetNdivisions(505)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(2)

    entries_sw = tree_sw.GetEntries()
    entries_fw = tree_fw.GetEntries()

    sw["bcid_prev"] = 0
    counter_sw_4096 = 0

    muons    = 0
    failures = 0

    for ent_sw in xrange(entries_sw):

        tree_sw.GetEntry(ent_sw)

        if tree_sw.hit_n == 0:
            continue

        # only one region for now
        correct_location = True
        for hit in xrange(int(tree_sw.hit_n)):
            if tree_sw.hit_station[hit] != station:
                correct_location = False
            strip = tree_sw.hit_strip[hit] - offset[int(tree_sw.hit_plane[hit])]
            if strip < region*512 or strip >= (region+1)*512:
                correct_location = False
        if not correct_location:
            continue
        else:
            muons += 1

        sw["mxl"]    = tree_sw.mxl
        sw["mxg"]    = tree_sw.my
        sw["mug"]    = tree_sw.mug
        sw["mvg"]    = tree_sw.mvg
        sw["dtheta"] = tree_sw.dtheta
        sw["phi"]    = tree_sw.phi
        sw["theta"]  = tree_sw.true_theta
        sw["bcid"]   = mode([bcid % 4096 for bcid in tree_sw.hit_bcid])
        if bcid_was_reset(sw["bcid"], sw["bcid_prev"]):
            counter_sw_4096 += 1
        sw["bcid_prev"] = sw["bcid"]

        matches        = 0
        diff["mxl"]    = []
        diff["mxg"]    = []
        diff["mug"]    = []
        diff["mvg"]    = []
        diff["dtheta"] = []
        diff["phi"]    = []
        diff["theta"]  = []

        fw["bcid_prev"] = 0
        counter_fw_4096 = 0

        for ent_fw in xrange(entries_fw):

            tree_fw.GetEntry(ent_fw)

            fw["mxl"]    = tree_fw.trig_mxl
            fw["mxg"]    = tree_fw.trig_mxg
            fw["mug"]    = tree_fw.trig_mug
            fw["mvg"]    = tree_fw.trig_mvg
            fw["dtheta"] = tree_fw.trig_dtheta
            fw["bcid"]   = tree_fw.trig_bcid
            fw["phi"]    = math.atan(tree_fw.trig_tanphi)
            fw["theta"]  = math.atan(tree_fw.trig_tantheta)

            if bcid_was_reset(fw["bcid"], fw["bcid_prev"]):
                counter_fw_4096 += 1
            fw["bcid_prev"] = fw["bcid"]

            if counter_fw_4096 < counter_sw_4096:
                continue
            if counter_fw_4096 > counter_sw_4096:
                break

            if bcid_match(sw["bcid"], fw["bcid"]) and counter_sw_4096==counter_fw_4096:
                matches += 1
                diff["mxl"]   .append(fw["mxl"]    - sw["mxl"])
                diff["mxg"]   .append(fw["mxg"]    - sw["mxg"])
                diff["mug"]   .append(fw["mug"]    - sw["mug"])
                diff["mvg"]   .append(fw["mvg"]    - sw["mvg"])
                diff["dtheta"].append(fw["dtheta"] - sw["dtheta"])
                diff["phi"]   .append(fw["phi"]    - sw["phi"])
                diff["theta"] .append(fw["theta"]  - sw["theta"])

        if matches > 0:
            hists["delta_mxl"]  .Fill(min(diff["mxl"],    key=abs))
            hists["delta_mxg"]  .Fill(min(diff["mxg"],    key=abs))
            hists["delta_mug"]  .Fill(min(diff["mug"],    key=abs))
            hists["delta_mvg"]  .Fill(min(diff["mvg"],    key=abs))
            hists["delta_dth"]  .Fill(min(diff["dtheta"], key=abs))
            hists["delta_phi"]  .Fill(min(diff["phi"],    key=abs))
            hists["delta_theta"].Fill(min(diff["theta"],  key=abs))
        else:
            announce_failure(tree_sw)
            failures += 1

        if matches > 0 and  min(diff["theta"], key=abs) > 0.01:
            print [bcid for bcid in tree_sw.hit_bcid], math.atan(tree_sw.my), math.atan(tree_fw.trig_mxg), tree_sw.theta, tree_sw.true_theta

        if False:
            print "%5i   %4i   %2i  %2i %8.4f %8.4f %8.4f %8.4f" % (muons, sw["bcid"], counter_sw_4096, len(diff["mxl"]), 
                                                                    min(diff["mxl"],    key=abs) if matches > 0 else 0,
                                                                    min(diff["mxg"],    key=abs) if matches > 0 else 0,
                                                                    min(diff["mug"],    key=abs) if matches > 0 else 0,
                                                                    min(diff["mvg"],    key=abs) if matches > 0 else 0,
                                                                    min(diff["dtheta"], key=abs) if matches > 0 else 0,
                                                                    min(diff["phi"],    key=abs) if matches > 0 else 0,
                                                                    min(diff["theta"],  key=abs) if matches > 0 else 0,
                                                                    )


    for name in hists:
        write_plot(name, hists[name], failures, muons)

def write_plot(name, hist, failures, muons):

    if False:
        fit = ROOT.TF1("fit_%s" % (hist.GetName()), "gaus(0)", -0.005, 0.005)
        hist.Fit(fit, "RWQN")
        fit.SetLineColor(ROOT.kBlack)
        fit.SetLineWidth(2)
        fit.SetLineStyle(7)
        fit.Draw("same")
    else:
        mean = hist.GetMean()
        rms  = hist.GetRMS()

    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Draw()
    rootutils.show_overflow(hist)
    hist.SetMinimum(0)
    hist.Draw("histsame")

    underflow = hist.GetBinContent(1)
    overflow  = hist.GetBinContent(hist.GetNbinsX())

    failure_top = ROOT.TLatex(0.70, 0.75, "fit failures")
    failure_bot = ROOT.TLatex(0.70, 0.70, "%i / %i = %.1f%%" % (failures, muons, 100*float(failures)/float(muons)))
    diagnostic_muons     = ROOT.TLatex(0.90, 0.80, "input muons: %i"           % (muons))
    diagnostic_failure   = ROOT.TLatex(0.90, 0.75,      "no fit: %3i, %4.1f%%" % (failures,  100*float(failures) /float(muons)))
    diagnostic_underflow = ROOT.TLatex(0.90, 0.70,   "underflow: %3i, %4.1f%%" % (underflow, 100*float(underflow)/float(muons)))
    diagnostic_overflow  = ROOT.TLatex(0.90, 0.65,    "overflow: %3i, %4.1f%%" % (overflow,  100*float(overflow) /float(muons)))
    diagnostic_mean      = ROOT.TLatex(0.90, 0.60,        "mean: %7.5f"        % (hist.GetMean()))
    diagnostic_rms       = ROOT.TLatex(0.90, 0.55,         "RMS: %7.5f"        % (hist.GetRMS()))
    
    for logo in [diagnostic_muons, diagnostic_failure, diagnostic_underflow, diagnostic_overflow, diagnostic_mean, diagnostic_rms]:
        logo.SetNDC()
        logo.SetTextAlign(32)
        logo.SetTextSize(0.025)
        logo.SetTextFont(82)
        logo.Draw()

    hist.SetMinimum(0.3)
    ROOT.gPad.SetLogy()
    
    canvas.SaveAs(canvas.GetName()+".pdf")

def mode(li):
    return max(set(li), key=li.count)

def bcid_was_reset(bcid, bcid_prev):
    # NB: BCIDs need to otherwise be in order
    return bcid < bcid_prev

def bcid_match(sw, fw):
    return fw - sw > 0 and fw - sw < 5

def announce_failure(tree):
    print
    print "Fit failed! mxlocal = %f, n(hits) = %i" % (tree.mxl, tree.hit_n)
    print

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
