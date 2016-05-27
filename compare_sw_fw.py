import sys
import rootutils,rootlogon
import ROOT
ROOT.gROOT.SetBatch()

filename_sw = "ntuple_sw.root"
filename_fw = "ntuple_fw.root"

file_sw = ROOT.TFile.Open(filename_sw)
file_fw = ROOT.TFile.Open(filename_fw)

tree_sw = file_sw.Get("physics")
tree_fw = file_fw.Get("physics")

region  = 6
station = 1
offset  = [65, 65,  73,  73,  73,  73, 65, 65] if station==1 else [68, 68, 110, 110, 110, 110, 68, 68]

def main():

    hists = {}
    hists["delta_mxl"] = ROOT.TH1F("delta_mxl", ";#Deltam_{X}^{local}(FW - SW);Events", 100, -0.01, 0.01)

    for hist in hists.values():
        hist.Sumw2()
        hist.GetXaxis().SetNdivisions(505)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(2)

    entries_sw = 1000 # tree_sw.GetEntries()
    entries_fw = tree_fw.GetEntries()

    bcid_sw_prev    = 0
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

        mxl_sw    = tree_sw.mxl
        bcid_sw   = mode([bcid % 4096 for bcid in tree_sw.hit_bcid])
        if bcid_was_reset(bcid_sw, bcid_sw_prev):
            counter_sw_4096 += 1
        bcid_sw_prev = bcid_sw

        delta_mxls = []

        bcid_fw_prev    = 0
        counter_fw_4096 = 0

        for ent_fw in xrange(entries_fw):

            tree_fw.GetEntry(ent_fw)

            mxl_fw  = tree_fw.trig_mxl
            bcid_fw = tree_fw.trig_bcid

            if bcid_was_reset(bcid_fw, bcid_fw_prev):
                counter_fw_4096 += 1
            bcid_fw_prev = bcid_fw

            if counter_fw_4096 < counter_sw_4096:
                continue
            if counter_fw_4096 > counter_sw_4096:
                break

            if bcid_match(bcid_sw, bcid_fw) and counter_sw_4096==counter_fw_4096:
                delta_mxls.append(mxl_fw - mxl_sw)


        if len(delta_mxls) > 0:
            hists["delta_mxl"].Fill(min(delta_mxls))
        else:
            announce_failure(tree_sw)
            failures += 1

        print "%5i   %4i   %2i   %s" % (muons, bcid_sw, counter_sw_4096, len(delta_mxls))

    canvas = ROOT.TCanvas("delta_mxl", "delta_mxl", 800, 800)
    canvas.Draw()
    rootutils.show_overflow(hists["delta_mxl"])
    hists["delta_mxl"].SetMinimum(0)
    hists["delta_mxl"].Draw("histsame")

    underflow = hists["delta_mxl"].GetBinContent(1)
    overflow  = hists["delta_mxl"].GetBinContent(hists["delta_mxl"].GetNbinsX())

    failure_top = ROOT.TLatex(0.70, 0.75, "fit failures")
    failure_bot = ROOT.TLatex(0.70, 0.70, "%i / %i = %.1f%%" % (failures, muons, 100*float(failures)/float(muons)))
    diagnostic_muons     = ROOT.TLatex(0.90, 0.80,     "muons: %i"           % (muons))
    diagnostic_failure   = ROOT.TLatex(0.90, 0.75,    "no fit: %3i, %4.1f%%" % (failures,  100*float(failures) /float(muons)))
    diagnostic_underflow = ROOT.TLatex(0.90, 0.70, "underflow: %3i, %4.1f%%" % (underflow, 100*float(underflow)/float(muons)))
    diagnostic_overflow  = ROOT.TLatex(0.90, 0.65,  "overflow: %3i, %4.1f%%" % (overflow,  100*float(overflow) /float(muons)))

    for logo in [diagnostic_muons, diagnostic_failure, diagnostic_underflow, diagnostic_overflow]:
        logo.SetNDC()
        logo.SetTextAlign(32)
        logo.SetTextSize(0.025)
        logo.SetTextFont(82)
        logo.Draw()

    hists["delta_mxl"].SetMinimum(0.3)
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
