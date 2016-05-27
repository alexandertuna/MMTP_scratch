import ROOT
ROOT.gROOT.SetBatch()

input_data = "hits_Ev309.txt"
nplanes = 8

class Hit:
    pass

def rootlogon():
    from ROOT import gStyle
    gStyle.SetOptStat(0)
    gStyle.SetPadTopMargin(0.07)
    gStyle.SetPadRightMargin(0.05)
    gStyle.SetPadBottomMargin(0.13)
    gStyle.SetPadLeftMargin(0.19)
    gStyle.SetTitleOffset(1.2, 'x')
    gStyle.SetTitleOffset(1.8, 'y')
    gStyle.SetTextSize(0.05)
    gStyle.SetLabelSize(0.05, 'xyz')
    gStyle.SetTitleSize(0.05, 'xyz')
    gStyle.SetTitleSize(0.05, 't')
    gStyle.SetPadTickX(1)
    gStyle.SetPadTickY(1)

def plane(number):
    if number == 0: return "x"
    if number == 1: return "x"
    if number == 2: return "u"
    if number == 3: return "v"
    if number == 4: return "u"
    if number == 5: return "v"
    if number == 6: return "x"
    if number == 7: return "x"
rootlogon()

hits = []

for line in open(input_data).readlines():
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

x_graph = ROOT.TGraph()
u_graph = ROOT.TGraph()
v_graph = ROOT.TGraph()

for color, gr in zip([ROOT.kBlack, ROOT.kBlue, 210],
                     [x_graph,     u_graph,    v_graph]):
    gr.SetMarkerColor(color)
    gr.SetLineColor(color)
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(1.4)

for hit in hits:
    #if plane(hit.plane) == "x": x_graph.SetPoint(x_graph.GetN(), hit.plane, hit.strip)
    #if plane(hit.plane) == "u": u_graph.SetPoint(u_graph.GetN(), hit.plane, hit.strip)
    #if plane(hit.plane) == "v": v_graph.SetPoint(v_graph.GetN(), hit.plane, hit.strip)

    if plane(hit.plane) == "x": x_graph.SetPoint(x_graph.GetN(), hit.plane, hit.slope)
    if plane(hit.plane) == "u": u_graph.SetPoint(u_graph.GetN(), hit.plane, hit.slope)
    if plane(hit.plane) == "v": v_graph.SetPoint(v_graph.GetN(), hit.plane, hit.slope)

canvas = ROOT.TCanvas("canvas_3x3s", "canvas_3x3s", 800, 800)
canvas.Draw()

multi = ROOT.TMultiGraph()
for gr in [x_graph, u_graph, v_graph]:
    multi.Add(gr, "PZ")

# minimum, maximum = 0.95*min([hit.strip for hit in hits]), 1.05*max([hit.strip for hit in hits])
minimum, maximum = 0.95*min([hit.slope for hit in hits]), 1.05*max([hit.slope for hit in hits])

# multi.SetTitle("; plane ; strip number")
multi.SetTitle("; plane ; hit slope")
multi.SetMinimum(minimum)
multi.SetMaximum(maximum)
multi.Draw("A")
multi.GetXaxis().SetLabelColor(0)
multi.GetXaxis().SetLimits(-0.5, 7.5)
multi.Draw("A")

expression = "[0] + [1]*x"
x_fit = ROOT.TF1("fit", expression, -0.5, nplanes+0.5)
x_graph.Fit(x_fit, "RWQN")

x_fit.SetLineColor(ROOT.kBlack)
x_fit.SetLineWidth(2)
x_fit.SetLineStyle(9)
x_fit.Draw("same")

labels = []
for pl in xrange(nplanes):
    label = ROOT.TLatex(pl/10.55 + 0.225, 0.08, plane(pl))
    label.SetTextSize(0.06)
    label.SetTextFont(42)
    label.SetNDC()
    label.Draw()
    labels.append(label)

canvas.SaveAs(canvas.GetName()+".pdf")


