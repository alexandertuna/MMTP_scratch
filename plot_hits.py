import copy
import os
import ROOT, rootlogon
ROOT.gROOT.SetBatch()

input = "data_text/hits_Ev309.txt"
var   = "strip"

nplanes = 8

def main():

    hits = read_hits(input)
    graph = {"x": ROOT.TGraph(), "u": ROOT.TGraph(), "v": ROOT.TGraph()}

    y_values = []
    for hit in hits:
        pl, hit_var = plane(hit.plane), getattr(hit, var)
        graph[pl].SetPoint(graph[pl].GetN(), hit.plane, hit_var)
        y_values.append(hit_var)

    name = "hit_%s_%s" % (os.path.basename(input).replace(".txt", ""), var)
    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Draw()
        
    multi = ROOT.TMultiGraph()
    for pl in graph:
        graph[pl].SetMarkerColor(color(pl))
        graph[pl].SetLineColor(color(pl))
        graph[pl].SetMarkerStyle(20)
        graph[pl].SetMarkerSize(1.4)
        multi.Add(graph[pl], "PZ")

    minimum = 0.95*min(y_values)
    maximum = 1.05*max(y_values)

    multi.SetTitle("; plane ; hit %s" % var)
    multi.SetMinimum(minimum)
    multi.SetMaximum(maximum)
    multi.Draw("A")
    multi.GetXaxis().SetLabelColor(0)
    multi.GetXaxis().SetLimits(-0.5, 7.5)
    multi.Draw("A")

    if var in ["slope", "strip"]:
        expression = "[0] + [1]*x"
        fit = ROOT.TF1("fit", expression, -0.5, nplanes+0.5)
        graph["x"].Fit(fit, "RWQN")
        
        fit.SetLineColor(ROOT.kBlack)
        fit.SetLineWidth(2)
        fit.SetLineStyle(9)
        fit.Draw("same")
    
    labels = []
    for pl in xrange(nplanes):
        label = ROOT.TLatex(pl/10.55 + 0.225, 0.08, plane(pl))
        label.SetTextSize(0.06)
        label.SetTextFont(42)
        label.SetNDC()
        label.Draw()
        labels.append(label)
    
    canvas.SaveAs(canvas.GetName()+".pdf")

def read_hits(input):

    hits = []

    for line in open(input).readlines():
        line = line.strip()
        if line.startswith("#"): continue
        if line.startswith("%"): continue
        if line.startswith("-"): continue
        if not line:             continue
        hit = Hit()

        _time, _vmm, _plane, _station, _strip, _slope = line.split()
        hit.time    = float(_time)
        hit.vmm     = int(_vmm)
        hit.plane   = int(_plane)
        hit.station = int(_station)
        hit.strip   = int(_strip)
        hit.slope   = float(_slope)
        
        if hit.strip > 0:
            hits.append(hit)

    return hits

class Hit:
    pass

def color(pl):
    if pl in ["x", "X"]: return ROOT.kBlack
    if pl in ["u", "U"]: return ROOT.kBlue
    if pl in ["v", "V"]: return 210

def plane(number):
    if number == 0: return "x"
    if number == 1: return "x"
    if number == 2: return "u"
    if number == 3: return "v"
    if number == 4: return "u"
    if number == 5: return "v"
    if number == 6: return "x"
    if number == 7: return "x"

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()


