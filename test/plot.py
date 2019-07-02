# To Run: python plot.py /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/ compareReemulRecoSeverity9/tps 1

# Edited by: gillian kopp [2019] for TP timing and depth studies
# Code from: yuan chen

# workflow: HcalCompareUpgradeChains.cc and analyze_run3.py, outputs analyze.root. run.C, outputs output_histograms.root, move both to FilesToPlot. Then run this code (plot.py)
# need to do cmsenv first to point toward the right source files   
# python plot.py /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/ compareReemulRecoSeverity9/tps 1  

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

#constraint = " && lumi > 32 && lumi < 1155"
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
folder = "./outPlots_fraction/"
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
path1 = "/afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/"
path2 = "/afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/FilesToPlot/"
mode = 1  # 1 means energy fraction versus depth, 2 means the RecHit/TP versus energy
out1 = "output_histograms.root"
out2 = "output_histograms2.root"

# start defining functions
def processData(path, out, mode):
  print('./run '+path+' '+out+' '+str(mode))
  # this is running the ./run executable that results from the run.C file
  status = os.system('./run '+path+' '+out+' '+str(mode))
  print(path+" finished")
  return status

if not process == 0:
  print("Generating histograms from NTuples, please wait a while...")
  #proc1 = multiprocessing.Process(target=processData, args=(path1,out1,mode))
  #proc1.start()
  #proc1.join()
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
      print("./run {} {} {}".format(group, _outf, mode))
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

r.gStyle.SetTitleFontSize(.5)
r.gStyle.SetTitleXSize(.5)
r.gStyle.SetTitleYSize(.5)
r.gStyle.SetPadBottomMargin(.06)
r.gStyle.SetPadLeftMargin(.08)
r.gStyle.SetPadRightMargin(.12)
r.gStyle.SetPadTopMargin(.06)

def getHists(name, f1, f2, ymax=1, title=0):
  yMax = 0
  print name
  #print "HI"
  #f1.Print()
  #[print key.GetName() for key in keys]
  #print f1.GetListOfKeys()
  t1 = f1.Get(name)
  t2 = f2.Get(name)
  t1.Draw()
  t1_p = t1.ProfileX(name+"_1")
  #t1_p.SetTitle(name+";Depth;Fraction")
  t2_p = t2.ProfileX(name+"_2")
  #print t1.GetName()
  if t1_p.GetMaximum() > t2_p.GetMaximum():
    yMax = t1_p.GetMaximum()
  else:
    yMax = t2_p.GetMaximum()
  if ymax:
    yMax = 2
  else:
    yMax = yMax * 1.2
  #print("T1: {}, TP: {}, yMax: {}".format(t1_p.GetMaximum(),t2_p.GetMaximum(),yMax))
  t1_p.SetLineColor(1)
  t1_p.SetLineWidth(2)
  t1_p.SetMarkerColor(1)
  t1_p.SetMarkerStyle(20)
  t1_p.SetAxisRange(0,min(yMax,1.05),"Y")
  t2_p.SetLineColor(2)
  t2_p.SetLineWidth(2)
  t2_p.SetMarkerColor(2)
  t2_p.SetMarkerStyle(20)
  t2_p.SetAxisRange(0,min(yMax,1.05),"Y")
  t1_p.SetTitle("")
  t2_p.SetTitle("")
  if not title:
    t1_p.GetXaxis().SetLabelSize(0.06)
    t1_p.GetYaxis().SetLabelSize(0.06)
    t2_p.GetXaxis().SetLabelSize(0.06)
    t2_p.GetYaxis().SetLabelSize(0.06)

  return t1_p, t2_p

def getHists3D(name, f):
  t = f.Get(name)
  t_p = t.Project3DProfile("yx")
  t_p.SetAxisRange(0,4,"Z")
  t_p.SetTitle("")
  return t_p


output = "TPFractionDepth_HE"
outfile = folder + output + ".pdf"
c = r.TCanvas()
c.SaveAs(outfile + '[')

Energy_Depth_n = "Energy_Depth_HE"
Energy_Depth_t1_p, Energy_Depth_t2_p = getHists(Energy_Depth_n, f1, f2, 0, 1)

Energy_Depth_t1_p.Draw("ehist")
outpics = folder + output + "1.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)
c.Update()
c = r.TCanvas()
Energy_Depth_t2_p.Draw("ehist")
outpics = folder + output + "2.eps"
c.SaveAs(outpics)
c.SaveAs(outfile)

c = r.TCanvas()
#r.gPad.SetGridx(r.kTRUE)
#r.gPad.SetGridy(r.kTRUE)
Energy_Depth_t1_p.Draw("ehist")
Energy_Depth_t2_p.Draw("ehistsame")
leg = r.TLegend(0.75,0.85,0.95,0.95)
#leg.AddEntry(Energy_Depth_t1_p,"Normal Run")
leg.AddEntry(Energy_Depth_t1_p,"0 PU MC")
leg.AddEntry(Energy_Depth_t2_p,"PU MC")
#leg.AddEntry(Energy_Depth_t2_p,"HighPU Run")
leg.Draw("same")
c.SaveAs(outfile)
outpics = folder + output + "_com.eps"
c.SaveAs(outpics)


for energy in range(1,4):
  print("Processing the energy range {}".format(energy))
  c = r.TCanvas()
  c.Update()
  c.Divide(4,3,0.01,0.01)
  num = 1
  for eta in range(17,29):
    c.cd(num)
    r.gPad.SetGridx(r.kTRUE)
    r.gPad.SetGridy(r.kTRUE)
    Energy_Depth_eta_en = "Fraction_Depth_HE_Abs(eta){}_{}".format(eta,energy)
    Energy_Depth_t1_p, Energy_Depth_t2_p = getHists(Energy_Depth_eta_en, f1, f2)
    Energy_Depth_t1_p.Draw("ehist")
    Energy_Depth_t2_p.Draw("ehistsame")
    num = num + 1
  c.cd()
  #leg = r.TLegend(0.9,1.0,0.9,0.95)
  #leg.AddEntry(Energy_Depth_t1_p,"Normal Run")
  #leg.AddEntry(Energy_Depth_t2_p,"HighPU Run")
  #leg.Draw("same")
  c.SaveAs(outfile)
  c.SaveAs(folder+"Fraction_Depth_{}.eps".format(energy))

# Plotting energy in depth and ieta profile
tp_depth_eta_n = "tp_depth_eta_HE"
c = r.TCanvas()
r.gPad.SetGridx(r.kTRUE)
r.gPad.SetGridy(r.kTRUE)
#r.gPad.SetLogz(True)
tp_depth_eta_t1 = getHists3D(tp_depth_eta_n, f1)
tp_depth_eta_t1.Draw("colz")
#tp_depth_eta_t1.Draw()
c.SaveAs(outfile)
c.SaveAs(folder+tp_depth_eta_n+"_1.eps")
c = r.TCanvas()
r.gPad.SetGridx(r.kTRUE)
r.gPad.SetGridy(r.kTRUE)
#r.gPad.SetLogz(True)
tp_depth_eta_t2 = getHists3D(tp_depth_eta_n, f2)
tp_depth_eta_t2.Draw("colz")
#tp_depth_eta_t2.Draw()
c.SaveAs(outfile)
c.SaveAs(folder+tp_depth_eta_n+"_2.eps")

c.SaveAs(outfile + ']')
print outfile +  " dumped..."
elapsed = time.clock() - start
print "Has used: " + str(elapsed) + " CPU secs"

print "All Done, please check output"
