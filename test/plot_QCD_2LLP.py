# Edited by: gillian kopp [2019] for TP timing and depth studies
# Code from: yuan chen

# workflow: HcalCompareUpgradeChains.cc and analyze_run3.py, outputs analyze.root. run.C, outputs output_histograms.root, move both to FilesToPlot. Then run this code (plot_simple.py)
# need to do cmsenv first to point toward the right source files   
# python plot_simple.py /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/ compareReemulRecoSeverity9/tps 1  

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

# if using input arguments, this will state how they should be listed
#if len(sys.argv) < 3:
#  print "Invalid input! Needs three parameters:"
#  print "The first parameter is the path where your Tuple stores"
#  print "The second parameter is the tree path in the Tuple, say compare/tps"
#  print "The third parameter is the number of files you want to run, non-positive number means all files under the path"
#  print "Here is an example to run:"
#  print "python plot.py /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot compareReemulRecoSeverity9/tps 1"
#  exit()

process = 0
if len(sys.argv) > 1: process=sys.argv[1]
start = time.clock()
#_detector = {'hb':"(abs(ieta)<=16)" ,'he': "(abs(ieta)>=16 && abs(ieta)<=29)",'hf':"(abs(ieta)>29)"}
#_constrain = [" && etsum > 0.5 && etsum <= 10"," && etsum > 10 && etsum <= 30"," && etsum > 30"]

# this is directory where the output plots will be stored
folder = "./outPlots_fraction_QCD_LLP_overlay/"
try:
  os.makedirs(folder)
except OSError:
  pass 

r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)

# input the path to the histogram files from run.C - either list path, or use system arguments
# path is where the root files (output of run.C and analyze_run3.py are)
# output is the output root file of the previous run.C
#path = sys.argv[1]
#tree_path = sys.argv[2]
#num = sys.argv[3]
path1 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins/"
path2 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh2000_mx975_pl500_ev1000/"
path3 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh125_mx50_pl500_ev1000/"
mode = 1  # 1 means energy fraction versus depth, 2 means the RecHit/TP versus energy
out1 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins/output_histograms_QCD_2bins.root"
out2 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh2000_mx975_pl500_ev1000/output_histograms_LLP_mh2000_mx975_pl500_ev1000.root"
out3 = "/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh125_mx50_pl500_ev1000/output_histograms_LLP_mh125_mx50_pl500_ev1000.root"

# start defining functions
def processData(path, out, mode):
  print('./run_2bins '+path+' '+out+' '+str(mode))
  # this is running the ./run_2bins executable that results from the run.C file
  status = os.system('./run_2bins '+path+' '+out+' '+str(mode))
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
      print("./run_2bins {} {} {}".format(group, _outf, mode))
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
      proc3 = multiprocessing.Process(target=processData, args=(path3,out3,mode))
      proc1.start()
      proc1.join()
      proc2.join()

print("Plotting histograms...")
f1 = r.TFile(out1)
f2 = r.TFile(out2)
f3 = r.TFile(out3)
if (f1.IsZombie() or (not f1.IsOpen())):
  print FAIL + "Error: cannot open " + out1 + " or the file is not valid,please check if filename is valid!" + END
if (f2.IsZombie() or (not f2.IsOpen())):
  print FAIL + "Error: cannot open " + out2 + " or the file is not valid,please check if filename is valid!" + END
if (f3.IsZombie() or (not f3.IsOpen())):
  print FAIL + "Error: cannot open " + out3 + " or the file is not valid,please check if filename is valid!" + END

r.gStyle.SetTitleFontSize(0.1)
r.gStyle.SetTitleXSize(0.1)
r.gStyle.SetTitleYSize(0.1)
r.gStyle.SetPadBottomMargin(.08)
r.gStyle.SetPadLeftMargin(.1)
r.gStyle.SetPadRightMargin(.12)
r.gStyle.SetPadTopMargin(.12)

def getHists(name, f1, f2, f3,  ymax=1, title=0):
  yMax = 0
  t1 = f1.Get(name)
  t2 = f2.Get(name)
  t3 = f3.Get(name)
  t1.Draw()
  t1_p = t1.ProfileX(name+"_1")
  t2_p = t2.ProfileX(name+"_2")
  t3_p = t3.ProfileX(name+"_3")
  if t1_p.GetMaximum() > t2_p.GetMaximum() and t1_p.GetMaximum() > t3_p.GetMaximum():
    yMax = t1_p.GetMaximum()
  elif t2_p.GetMaximum() > t3_p.GetMaximum():
    yMax = t2_p.GetMaximum()
  else:
    yMax = t3_p.GetMaximum()
  if ymax:
    yMax = 3
  else:
    yMax = yMax * 1.2
  t1_p.SetLineColor(2)
  t1_p.SetLineWidth(2)
  t1_p.SetMarkerColor(2)
  t1_p.SetMarkerStyle(20)
  t1_p.SetAxisRange(0,min(yMax,1.05),"Y")
#  t2_p.SetLineColor(920)
  t2_p.SetLineColor(1)
  t2_p.SetLineWidth(2)
#  t2_p.SetMarkerColor(920)
  t2_p.SetMarkerColor(1)
  t2_p.SetMarkerStyle(20)
  t2_p.SetAxisRange(0,min(yMax,1.05),"Y")
  t3_p.SetLineColor(921)
#  t3_p.SetLineColor(3)
  t3_p.SetLineWidth(2)
  t3_p.SetMarkerColor(921)
#  t3_p.SetMarkerColor(3)
  t3_p.SetMarkerStyle(20)
  t3_p.SetAxisRange(0,min(yMax,1.05),"Y")

  t1_p.SetTitle("")
  t2_p.SetTitle("")
  t1_p.SetTitleOffset(0.8,"x")
  t2_p.SetTitleOffset(0.8,"x")
  t1_p.SetTitleOffset(1.2,"y")
  t2_p.SetTitleOffset(1.2,"y")
  t1_p.SetTitleSize(0.035,"xyz")
  t2_p.SetTitleSize(0.035,"xyz")
  if not title:
    t1_p.GetXaxis().SetLabelSize(0.06)
    t1_p.GetYaxis().SetLabelSize(0.06)
    t2_p.GetXaxis().SetLabelSize(0.06)
    t2_p.GetYaxis().SetLabelSize(0.06)

  return t1_p, t2_p, t3_p

def getHists3D(name, f):
  t = f.Get(name)
  t_p = t.Project3DProfile("yx")
  t_p.SetAxisRange(0,4,"Z")
  t_p.SetTitle("")
  return t_p

# ********************************************************* 
# plots for the ENDCAP region of fractional depth, inclusive
# also adding in energy bins
output = "TPFractionDepth_HE"
outfile = folder + output + ".pdf"
c = r.TCanvas()
c.SaveAs(outfile + '[')

Energy_Depth_n = "Energy_Depth_HE"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t1_p.SetTitle("HCAL Endcap, Inclusive, QCD")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
outpics = folder + output + "1.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)
c.Update()

c = r.TCanvas()
Energy_Depth_t2_p.Draw("ehist")
Energy_Depth_t2_p.SetTitle("HCAL Endcap, Inclusive, LLP mh = 2000 GeV")
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
outpics = folder + output + "2.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)

c = r.TCanvas()
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Endcap, Inclusive")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)             
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com.eps"
c.SaveAs(outpics)

# adding for the inclusive regions, separated in energy bins
c = r.TCanvas()
Energy_Depth_n = "Energy_Depth_HE_0510"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Endcap, Inclusive, TP ET 0.5-10 GeV")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com_lowET.eps"
c.SaveAs(outpics)

c = r.TCanvas()
Energy_Depth_n = "Energy_Depth_HE_10"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Endcap, Inclusive, TP ET 10+ GeV")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com_highET.eps"
c.SaveAs(outpics)

# *********************************************************
# plots for the BARREL region of fractional depth, inclusive
# also adding in splits for energy bins
output = "TPFractionDepth_HB"
outfile = folder + output + ".pdf"
c = r.TCanvas()
c.SaveAs(outfile + '[')

Energy_Depth_n = "Energy_Depth_HB"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t1_p.SetTitle("HCAL Barrel, Inclusive, QCD")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
outpics = folder + output + "1.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)
c.Update()

c = r.TCanvas()
Energy_Depth_t2_p.Draw("ehist")
Energy_Depth_t2_p.SetTitle("HCAL Barrel, Inclusive, LLP, mh=2000 GeV")
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
outpics = folder + output + "2.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)

c = r.TCanvas()
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Barrel, Inclusive")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com.eps"
c.SaveAs(outpics)

# adding for the inclusive regions, separated in energy bins                                                                          
c = r.TCanvas()
Energy_Depth_n = "Energy_Depth_HB_0510"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Barrel, Inclusive, TP ET 0.5-10 GeV")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com_lowET.eps"
c.SaveAs(outpics)

c = r.TCanvas()
Energy_Depth_n = "Energy_Depth_HB_10"
Energy_Depth_t1_p, Energy_Depth_t2_p, Energy_Depth_t3_p = getHists(Energy_Depth_n, f1, f2, f3, 0, 1)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
Energy_Depth_t3_p.Draw("ehistsame")
Energy_Depth_t1_p.SetTitle("HCAL Barrel, Inclusive, TP ET 10+ GeV")
Energy_Depth_t1_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t1_p.GetYaxis().SetTitle("TP energy fraction");
Energy_Depth_t2_p.GetXaxis().SetTitle("HCAL depth");
Energy_Depth_t2_p.GetYaxis().SetTitle("TP energy fraction");
leg = r.TLegend(0.75,0.75,0.95,0.85)
leg.AddEntry(Energy_Depth_t1_p,"QCD MC")
leg.AddEntry(Energy_Depth_t2_p,"LLP MC, mh=2000 GeV")
leg.AddEntry(Energy_Depth_t3_p,"LLP MC, mh=125 GeV")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com_highET.eps"
c.SaveAs(outpics)


c.SaveAs(outfile + ']')
print outfile +  " dumped..."
elapsed = time.clock() - start
print "Has used: " + str(elapsed) + " CPU secs"

print "All Done, please check output"
