# Edited by: gillian kopp [2019] for TP timing and depth studies
# Code from: yuan chen

# workflow: HcalCompareUpgradeChains.cc and analyze_run3.py, outputs analyze.root. run.C, outputs output_histograms.root, move both to FilesToPlot. Then run this code (plot_simple.py)
# need to do cmsenv first to point toward the right source files   
# python plot_simple.py /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/ compareReemulRecoSeverity9/tps 1  
# this is specifically designed for plotting pulse shapes, resulting from run_pulse_shape.C
# plot_pulse_shape_overlay is for overlaying the average of two samples (QCD, LLP)

# import statements
import ROOT as r
import datetime
import sys
import commands
import os
import multiprocessing
import threading
import time

HEADER   = '\033[95m'
BLUE     = '\033[94m'
GREEN    = '\033[92m'
WARNING  = '\033[93m'
FAIL     = '\033[91m'
BOLD     = '\033[1m'
UNDERLINE= '\033[4m'
END      = '\033[0m'

constraint = ""
timestamp = datetime.datetime.now().strftime("%H:%M:%S")

process = 0
if len(sys.argv) > 1: process=sys.argv[1]
start = time.clock()
#_detector = {'hb':"(abs(ieta)<=16)" ,'he': "(abs(ieta)>=16 && abs(ieta)<=29)",'hf':"(abs(ieta)>29)"}
#_constrain = [" && etsum > 0.5 && etsum <= 10"," && etsum > 10 && etsum <= 30"," && etsum > 30"]

# this is directory where the output plots will be stored
folder = "./outPlots_pulse_shape_overlay/"
try:
  os.makedirs(folder)
except OSError:
  pass 

r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)

#path1 = "/afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/"
path1 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/EnergyDepth_2bins_0pt5_5/LLP_mh2000_mx975_pl10000_ev1000/"
path2 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins_0pt5_5/"
mode = 1  # 1 means energy fraction versus depth, 2 means the RecHit/TP versus energy
#out1 = "/afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/output_histograms_ps_mh2000_mx975_pl10000_ev1000.root"
out1 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/EnergyDepth_2bins_0pt5_5/LLP_mh2000_mx975_pl10000_ev1000/output_histograms_ps_mh2000_mx975_pl10000_ev1000.root"
out2 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins_0pt5_5/output_histograms_ps_QCD.root"

# start defining functions
def processData(path, out, mode):
  print('./run_pulse_shape '+path+' '+out+' '+str(mode))
  # this is running the ./run_pulse_shape executable that results from the run_pulse_shape.C file
  status = os.system('./run_pulse_shape '+path+' '+out+' '+str(mode))
  print(path+" finished")
  return status

if not process == 0:
  print("Generating histograms from NTuples, please wait a while...")
  proc2 = multiprocessing.Process(target=processData, args=(path2,out2,mode))
  proc2.start()
  # processing the first path
  _files = [f for f in os.listdir(path1) if f.endswith(".root")]
  _numf = len(_files)
  if _numf > 60: # too many files, we launch multiple processes to do them
    _current = os.getcwd()
    os.chdir(path1)
    for _num in range(1,12):
      _dir = "Group" + str(_num)
      os.system("mkdir -p ./" + _dir)
      for _mvf in _files[0:min(_numf/10,len(_files))]:
        os.system("mv " + _mvf + " ./" + _dir)
        _files.remove(_mvf)
    _ngroup = [path1+g+"/" for g in os.listdir(path1) if g.startswith("Group")]
    os.chdir(_current)
    _out = []
    _record = []
    _num = 0
    os.system("rm -rf ./1temp*.root")
    for group in _ngroup:
      _outf = "1temp{}.root".format(_num)
      _out.append(_outf)
      print("./run_pulse_shape {} {} {}".format(group, _outf, mode))
      thread = threading.Thread(target=processData, args=(group,_outf,mode))
      thread.start()
      _record.append(thread)
      _num = _num + 1
    for thread in _record:
      thread.join()
    proc2.join()
    os.system("rm -rf ./" + out1)
    os.system("hadd " + out1 + " 1temp*.root")
    os.system("rm -rf ./1temp*.root")
  else:
    _ngroup = [path1+g+"/" for g in os.listdir(path1) if g.startswith("Group")]
    if len(_ngroup) > 0:
      _out = [] 
      _record = []
      _num = 0
      os.system("rm -rf ./1temp*.root")
      for group in _ngroup:
        _outf = "1temp{}.root".format(_num)
        _out.append(_outf)
        thread = threading.Thread(target=processData, args=(group,_outf,mode))
        thread.start()
        _record.append(thread)
        _num = _num + 1 
      for thread in _record:
        thread.join()
      proc2.join()
      os.system("rm -rf ./" + out1)
      os.system("hadd " + out1 + " 1temp*.root")
      os.system("rm -rf ./1temp*.root")
    else:
      proc1 = multiprocessing.Process(target=processData, args=(path1,out1,mode))
      proc1.start()
      proc1.join()
      proc2.join()

print("Plotting histograms...")
f1 = r.TFile(out1)
f2 = r.TFile(out2)
if (f1.IsZombie() or (not f1.IsOpen())):
  print FAIL + "Error: cannot open " + out1 + " or the file is not valid,please check if filename is valid!" + END
if (f2.IsZombie() or (not f2.IsOpen())):
  print FAIL + "Error: cannot open " + out2 + " or the file is not valid,please check if filename is valid!" + END

r.gStyle.SetTitleFontSize(0.1)
r.gStyle.SetTitleXSize(0.1)
r.gStyle.SetTitleYSize(0.1)
r.gStyle.SetPadBottomMargin(.08)
r.gStyle.SetPadLeftMargin(.1)
r.gStyle.SetPadRightMargin(.12)
r.gStyle.SetPadTopMargin(.12)

def getHists(name, f1, f2, ymax=1, title=0):
  yMax = 0
  t1 = f1.Get(name)
  t2 = f2.Get(name)
  t1.Draw("colz")
  t1_p = t1.ProfileX(name+"_1")
  t2_p = t2.ProfileX(name+"_2")
  if t1_p.GetMaximum() > t2_p.GetMaximum():
    yMax = t1_p.GetMaximum()
  else:
    yMax = t2_p.GetMaximum()
  if ymax:
    yMax = 2
  else:
    yMax = yMax * 1.2

  t1_p.SetLineColor(1)
  t1_p.SetLineWidth(1)
  t1_p.SetMarkerColor(1)
  t1_p.SetMarkerStyle(20)
  t1_p.SetAxisRange(0,yMax,"Y")
  t2_p.SetLineColor(2)
  t2_p.SetLineWidth(1)
  t2_p.SetMarkerColor(2)
  t2_p.SetMarkerStyle(20)
  t2_p.SetAxisRange(0,yMax,"Y")

  t1_p.SetTitle("")
  t1_p.SetTitleOffset(0.8,"x")
  t1_p.SetTitleOffset(1.2,"y")
  t1_p.SetTitleSize(0.035,"xyz")

  t2_p.SetTitle("")
  t2_p.SetTitleOffset(0.8,"x")
  t2_p.SetTitleOffset(1.2,"y")
  t2_p.SetTitleSize(0.035,"xyz")

  if not title:
    t1_p.GetXaxis().SetLabelSize(0.06)
    t1_p.GetYaxis().SetLabelSize(0.06)
    t2_p.GetXaxis().SetLabelSize(0.06)
    t2_p.GetYaxis().SetLabelSize(0.06)

  return t1_p, t2_p

# for saving histograms and plots
output = "Pulse_Shape_HE"
outfile = folder + output + ".pdf"
c = r.TCanvas()
c.SaveAs(outfile + '[')

# ********************************************************* 
# plots for barrel and endcap regions, ieta and energy bins
# ENDCAP

for energy in range(1,4):
  print("Processing the energy range HE {}".format(energy))
  c = r.TCanvas()
  r.gStyle.SetPadBottomMargin(.12)
  r.gStyle.SetPadLeftMargin(.13)
  r.gStyle.SetPadRightMargin(.12)
  r.gStyle.SetPadTopMargin(.12)
  
  c.Update()
  c.Divide(4,3,0.01,0.01)
  num = 1
  for eta in range(17,29): # 17-28 are the endcap region
    c.cd(num)
    r.gPad.SetGridx(r.kTRUE)
    r.gPad.SetGridy(r.kTRUE)
    Pulse_Shape_eta_en_HE = "Pulse_Shape_HE_Abs(eta){}_{}".format(eta,energy)
    Pulse_Shape_t1_p, Pulse_Shape_t2_p = getHists(Pulse_Shape_eta_en_HE, f1, f2, 0, 1)
    Pulse_Shape_t1_p.Draw("colz")
    Pulse_Shape_t2_p.Draw("same")

    Pulse_Shape_t1_p.SetTitle("iEta {}".format(eta))
    Pulse_Shape_t1_p.GetXaxis().SetTitle("TS");
    Pulse_Shape_t1_p.GetYaxis().SetTitle("ADC");
    Pulse_Shape_t1_p.SetTitleSize(0.07,"xy")
    Pulse_Shape_t1_p.SetTitleOffset(0.8,"x")
    Pulse_Shape_t1_p.SetTitleOffset(0.85,"y")

    leg = r.TLegend(0.65,0.65,0.95,0.85)
    leg.AddEntry(Pulse_Shape_t1_p,"LLP MC")
    leg.AddEntry(Pulse_Shape_t2_p,"QCD MC")
    leg.Draw("same")

    num = num + 1
  c.cd()
#  c.SaveAs(outfile)
  c.SaveAs(folder+"Pulse_Shape_HE_{}.pdf".format(energy))


# for saving histograms and plots                                                                                                       
output = "Pulse_Shape_HB"
outfile = folder + output + ".pdf"
c = r.TCanvas()
c.SaveAs(outfile + '[')
# ********************************************************* 
# BARREL
for energy in range(1,4):
  print("Processing the energy range HB {}".format(energy))
  c = r.TCanvas()
  r.gStyle.SetPadBottomMargin(0.12)
  r.gStyle.SetPadLeftMargin(0.14) 
  r.gStyle.SetPadRightMargin(0.12)
  r.gStyle.SetPadTopMargin(0.12)

  c.Update()
  c.Divide(4,4,0.01,0.01)
  num = 1
  for eta in range(1,16): # 1-15 or 16 are the barrel region
    #print("HB event with ieta {}".format(eta))
    c.cd(num)
    r.gPad.SetGridx(r.kTRUE)
    r.gPad.SetGridy(r.kTRUE)
    Pulse_Shape_eta_en_HB = "Pulse_Shape_HB_Abs(eta){}_{}".format(eta,energy)
    #print("eta, energy {}, {}".format(eta,energy))
    Pulse_Shape_t1_p, Pulse_Shape_t2_p = getHists(Pulse_Shape_eta_en_HB, f1, f2, 0, 1)
    Pulse_Shape_t1_p.Draw("colz")
    Pulse_Shape_t2_p.Draw("same")

    Pulse_Shape_t1_p.SetTitle("iEta {}".format(eta))
    Pulse_Shape_t1_p.GetXaxis().SetTitle("TS");
    Pulse_Shape_t1_p.GetYaxis().SetTitle("ADC");
    Pulse_Shape_t1_p.SetTitleSize(0.09,"xy")
    Pulse_Shape_t1_p.SetTitleOffset(0.6,"x")
    Pulse_Shape_t1_p.SetTitleOffset(0.65,"y")

    leg = r.TLegend(0.65,0.65,0.95,0.85)
    leg.AddEntry(Pulse_Shape_t1_p,"LLP MC")
    leg.AddEntry(Pulse_Shape_t2_p,"QCD MC")
    leg.Draw("same")

    num = num + 1
  c.cd()
#  c.SaveAs(outfile)
  c.SaveAs(folder+"Pulse_Shape_HB_{}.pdf".format(energy))

# Plotting energy in depth and ieta profile                                                                                                   
#c.SaveAs(outfile + ']')
print outfile +  " dumped..."
elapsed = time.clock() - start
print "Has used: " + str(elapsed) + " CPU secs"

print "All Done, please check output"
