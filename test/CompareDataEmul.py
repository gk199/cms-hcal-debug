import os
import ROOT
import math
import argparse
import multiprocessing
from array import array

def fill(d,t):
    for b, h in d.iteritems():
        h.Fill(getattr(t,b))


#inputFile = ROOT.TFile.Open("analyze_345386.root")
inputFile = ROOT.TFile.Open("test/analyze_347746.root")

evtsTree = inputFile.Get("compare/tps")

branchNames =  ["soi",
		"soi_emul",
		"npresamples",
		"npresamples_emul",
		"ieta",
		"iphi",
		"et",
		"et_emul",
		"zsMarkAndPass",
		"zsMarkAndPass_emul",
		"fg0",
		"fg1",
		"fg2",
		"fg3",
		"fg4",
		"fg5",
		"fg6",
                "fg0_emul",
                "fg1_emul",
                "fg2_emul",
                "fg3_emul",
                "fg4_emul",
                "fg5_emul",
                "fg6_emul",
		"adc0",
		"adc1",
		"adc2",
		"adc3",
		"adc4",
		"adc5",
		"adc6",
		"adc7",
		"adc8",
		"adc9",
                "adc0_emul",
                "adc1_emul",
                "adc2_emul",
                "adc3_emul",
                "adc4_emul",
                "adc5_emul",
                "adc6_emul",
                "adc7_emul",
                "adc8_emul",
                "adc9_emul"]

branches = []
evtsTree.SetBranchStatus("*", 0)

for branchName in branchNames:
	evtsTree.SetBranchStatus(branchName, 1)
	branches.append(evtsTree.GetBranch(branchName))

histos = {
	"soi"			: ROOT.TH1F("soi","soi",90,0,450),
	"soi_emul"		: ROOT.TH1F("soi_emul","soi_emul",90,0,450),
	"soi_corr"		: ROOT.TH2F("soi_corr","soi",90,0,450,90,0,450),
#	"npresamples"		: ROOT.TH1F("npresamples","npresamples",100,0,100),
#	"npresamples_emul"	: ROOT.TH1F("npresamples_emul","npresamples_emul",100,0,100),
	"npresamples_corr"	: ROOT.TH2F("npresamples_corr","npresamples", 3, -0.5, 2.5, 3, -0.5, 2.5),
	"et"			: ROOT.TH1F("et","et",100,0,100),
	"et_emul"		: ROOT.TH1F("et_emul","et_emul",100,0,100),
        "et_corr"	        : ROOT.TH2F("et_corr","et",100,0,100,100,0,100),
        "et_corr13"	        : ROOT.TH2F("et_corr13","",128,0,128,128,0,128),
        "et_corr14"	        : ROOT.TH2F("et_corr14","",128,0,128,128,0,128),
        "et_corr15"	        : ROOT.TH2F("et_corr15","",128,0,128,128,0,128),
        "et_corr16"	        : ROOT.TH2F("et_corr16","",128,0,128,128,0,128),
        "et_corr17"	        : ROOT.TH2F("et_corr17","",128,0,128,128,0,128),
        "et_corr18"	        : ROOT.TH2F("et_corr18","",128,0,128,128,0,128),
        "et_corr19"	        : ROOT.TH2F("et_corr19","",128,0,128,128,0,128),
        "et_corr20"	        : ROOT.TH2F("et_corr20","",128,0,128,128,0,128),
#	"zsMarkAndPass"		: ROOT.TH1F("zsMarkAndPass","zsMarkAndPass",100,0,100),
#	"zsMarkAndPass_emul"	: ROOT.TH1F("zsMarkAndPass_emul","zsMarkAndPass_emul",100,0,100),
	"fg1"			: ROOT.TH1F("fg1","fg1",2,0,2),
	"fg1_emul"		: ROOT.TH1F("fg1_emul","fg1_emul",2,0,2),
        "fg1_corr"              : ROOT.TH2F("fg1_corr","fg1",2,0,2,2,0,2),
        "fg0_corr"              : ROOT.TH2F("fg0_corr","fg0",2,0,2,2,0,2),
        "fg2_corr"              : ROOT.TH2F("fg2_corr","fg2",2,0,2,2,0,2),
        "fg3_corr"              : ROOT.TH2F("fg3_corr","fg3",2,0,2,2,0,2),
        "fg4_corr"              : ROOT.TH2F("fg4_corr","fg4",2,0,2,2,0,2),
        "fg5_corr"              : ROOT.TH2F("fg5_corr","fg5",2,0,2,2,0,2),
        "fg6_corr"              : ROOT.TH2F("fg6_corr","fg6",2,0,2,2,0,2),
	"adc0"			: ROOT.TH1F("adc0","adc0",100,0,300),
        "adc0_emul"             : ROOT.TH1F("adc0_emul","adc0_emul",100,0,300),
        "adc0_corr"             : ROOT.TH2F("adc0_corr","adc0",60,-0.5,59.5,60,-0.5,59.5),
        "adc1"                  : ROOT.TH1F("adc1","adc1",100,0,300),
        "adc1_emul"             : ROOT.TH1F("adc1_emul","adc1_emul",100,0,300),
        "adc1_corr"             : ROOT.TH2F("adc1_corr","adc1",60,-0.5,59.5,60,-0.5,59.5),
#        "adc1_corr"             : ROOT.TH2F("adc1_corr","adc1_corr",8,-0.5,7.5,8,-0.5,7.5),
        "adc2"                  : ROOT.TH1F("adc2","adc2",100,0,300),
        "adc2_emul"             : ROOT.TH1F("adc2_emul","adc2_emul",100,0,300),
        "adc2_corr"             : ROOT.TH2F("adc2_corr","adc2",250,0,250,250,0,250),
#        "adc2_corr"             : ROOT.TH2F("adc2_corr","adc2_corr",8,-0.5,7.5,8,-0.5,7.5),
        "adc3"                  : ROOT.TH1F("adc3","adc3",100,0,300),
        "adc3_emul"             : ROOT.TH1F("adc3_emul","adc3_emul",100,0,300),
        "adc3_corr"             : ROOT.TH2F("adc3_corr","adc3",100,0,100,100,0,100),
#        "adc3_corr"             : ROOT.TH2F("adc3_corr","adc3_corr",8,-0.5,7.5,8,-0.5,7.5),
	"ieta_iphi"		: ROOT.TH2F("ieta_iphi", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg0"         : ROOT.TH2F("ieta_iphi_fg0", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg1"         : ROOT.TH2F("ieta_iphi_fg1", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg2"         : ROOT.TH2F("ieta_iphi_fg2", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg3"         : ROOT.TH2F("ieta_iphi_fg3", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg4"         : ROOT.TH2F("ieta_iphi_fg4", "", 90, -45, 45, 75, 0, 75),
        "ieta_iphi_fg5"         : ROOT.TH2F("ieta_iphi_fg5", "", 90, -45, 45, 75, 0, 75),
}


#evtsTree.Draw("soi>>soi")
#evtsTree.Draw("soi_emul>>soi_emul")
evtsTree.Draw("soi_emul:soi>>soi_corr")
#evtsTree.Draw("et>>et")
#evtsTree.Draw("et_emul>>et_emul")
#evtsTree.Draw("npresamples_emul:npresamples>>npresamples_corr")
evtsTree.Draw("et_emul:et>>et_corr")
#evtsTree.Draw("fg1>>fg1")
#evtsTree.Draw("fg1_emul>>fg1_emul")
evtsTree.Draw("fg0_emul:fg0>>fg0_corr", "abs(ieta) < 16")
evtsTree.Draw("fg1_emul:fg1>>fg1_corr", "abs(ieta) < 16")
evtsTree.Draw("fg2_emul:fg2>>fg2_corr", "abs(ieta) < 16")
evtsTree.Draw("fg3_emul:fg3>>fg3_corr", "abs(ieta) < 16")
evtsTree.Draw("fg4_emul:fg4>>fg4_corr", "abs(ieta) < 16")
evtsTree.Draw("fg5_emul:fg5>>fg5_corr", "abs(ieta) < 16")
evtsTree.Draw("fg6_emul:fg6>>fg6_corr", "abs(ieta) < 16")
#evtsTree.Draw("adc0>>adc0")
#evtsTree.Draw("adc0_emul>>adc0_emul")
#evtsTree.Draw("adc0_emul:adc0>>adc0_corr")
#evtsTree.Draw("adc1>>adc1")
#evtsTree.Draw("adc1_emul>>adc1_emul")
#evtsTree.Draw("adc1_emul:adc1>>adc1_corr")
#evtsTree.Draw("adc2>>adc2")
#evtsTree.Draw("adc2_emul>>adc2_emul")
#evtsTree.Draw("adc2_emul:adc2>>adc2_corr")
#evtsTree.Draw("adc3>>adc3")
#evtsTree.Draw("adc3_emul>>adc3_emul")
#evtsTree.Draw("adc3_emul:adc3>>adc3_corr")
#evtsTree.Draw("iphi:ieta>>ieta_iphi")
#evtsTree.Draw("iphi:ieta>>ieta_iphi","fg0_emul > fg0")
#evtsTree.Draw("iphi:ieta>>ieta_iphi","fg1_emul > fg1")
#evtsTree.Draw("iphi:ieta>>ieta_iphi","abs(soi-soi_emul) > 5")
#evtsTree.Draw("iphi:ieta>>ieta_iphi","npresamples_emul>npresamples && ieta !=17")
#evtsTree.Draw("iphi:ieta>>ieta_iphi")


#evtsTree.Draw("iphi:ieta>>ieta_iphi", "adc2+adc3!=adc2_emul+adc3_emul && abs(ieta) < 17")
#evtsTree.Draw("iphi:ieta>>ieta_iphi", "adc2+adc3!=adc2_emul+adc3_emul && et > 0")
#evtsTree.Draw("iphi:ieta>>ieta_iphi", "adc2+adc3==adc2_emul+adc3_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg0", "fg0!=fg0_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg1", "fg1!=fg1_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg2", "fg2!=fg2_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg3", "fg3!=fg3_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg4", "fg4!=fg4_emul && et > 0")
evtsTree.Draw("iphi:ieta>>ieta_iphi_fg5", "fg5!=fg5_emul && et > 0")
#evtsTree.Draw("iphi:ieta>>ieta_iphi", "soi==soi_emul && soi > 0")
#evtsTree.Draw("iphi:ieta>>ieta_iphi", "soi!=soi_emul && ieta < 0 && ((iphi > 18 && iphi < 23) || (iphi > 34 && iphi < 39))")
#evtsTree.Draw("iphi:ieta>>ieta_iphi", "et!=et_emul")
#evtsTree.Draw("et_emul:et>>et_corr13", "ieta==-19 && (iphi==35 || iphi==19)")
#evtsTree.Draw("et_emul:et>>et_corr14", "ieta==-9 && (iphi==36 || iphi==20)")
#evtsTree.Draw("et_emul:et>>et_corr15", "ieta==-9 && (iphi==37 || iphi==21)")
#evtsTree.Draw("et_emul:et>>et_corr16", "ieta==-9 && (iphi==38 || iphi==22)")
evtsTree.Draw("et_emul:et>>et_corr13", "ieta==-9 && (iphi==19)")
evtsTree.Draw("et_emul:et>>et_corr14", "ieta==-16 && (iphi==20)")
evtsTree.Draw("et_emul:et>>et_corr15", "ieta==-16 && (iphi==21)")
evtsTree.Draw("et_emul:et>>et_corr16", "ieta==-16 && (iphi==22)")
evtsTree.Draw("et_emul:et>>et_corr17", "ieta==9 && iphi==62")
evtsTree.Draw("et_emul:et>>et_corr18", "ieta==20 && iphi%4==1")
evtsTree.Draw("et_emul:et>>et_corr19", "ieta==20 && iphi%4==2")
evtsTree.Draw("et_emul:et>>et_corr20", "ieta==20 && iphi%4==3")

#for event in xrange(evtsTree.GetEntriesFast()):

#	evtsTree.GetEntry(event)
#	histos["soi"].Fill(evtsTree.soi)
#        histos["soi_emul"].Fill(evtsTree.soi_emul)
##        histos["npresamples"].Fill(evtsTree.npresamples)
##        histos["npresamples_emul"].Fill(evtsTree.npresamples_emul)
#        histos["et"].Fill(evtsTree.et)
#        histos["et_emul"].Fill(evtsTree.et_emul)
##        histos["zsMarkAndPass"].Fill(evtsTree.zsMarkAndPass)
##        histos["zsMarkAndPass_emul"].Fill(evtsTree.zsMarkAndPass_emul)
#        histos["fg1"].Fill(evtsTree.fg1)
#        histos["fg1_emul"].Fill(evtsTree.fg1_emul)
#        histos["adc0"].Fill(evtsTree.adc0)
#        histos["adc0_emul"].Fill(evtsTree.adc0_emul)

#for b, h in histos.iteritems():
#        h.SetStats(0)

#        for branch in branches:
#        	branch.GetEntry(event)

#	fill(histos,evtsTree)


c = ROOT.TCanvas("c","c",800,800)
histos["soi_corr"].Draw("colz")
histos["soi_corr"].GetYaxis().SetTitle("Emul")
histos["soi_corr"].GetXaxis().SetTitle("Data")
histos["soi_corr"].SetTitle("SOI energy emulator vs data")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/soi_corr.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr"].Draw("colz")
histos["et_corr"].GetYaxis().SetTitle("Emul")
histos["et_corr"].GetXaxis().SetTitle("Data")
histos["et_corr"].SetTitle("ET emulator vs data")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg0"].Draw("colz")
histos["ieta_iphi_fg0"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg0"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg0"].SetTitle("ieta vs iphi for fg0!=fg0_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg0.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg1"].Draw("colz")
histos["ieta_iphi_fg1"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg1"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg1"].SetTitle("ieta vs iphi for fg1!=fg1_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg1.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg2"].Draw("colz")
histos["ieta_iphi_fg2"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg2"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg2"].SetTitle("ieta vs iphi for fg2!=fg2_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg2.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg3"].Draw("colz")
histos["ieta_iphi_fg3"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg3"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg3"].SetTitle("ieta vs iphi for fg3!=fg3_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg3.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg4"].Draw("colz")
histos["ieta_iphi_fg4"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg4"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg4"].SetTitle("ieta vs iphi for fg4!=fg4_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg4.png")

c = ROOT.TCanvas("c","c",800,800)
histos["ieta_iphi_fg5"].Draw("colz")
histos["ieta_iphi_fg5"].GetYaxis().SetTitle("iphi")
histos["ieta_iphi_fg5"].GetXaxis().SetTitle("ieta")
histos["ieta_iphi_fg5"].SetTitle("ieta vs iphi for fg5!=fg5_emul && et > 0")
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/ietaViphi_fg5.png")

# fg bit data emulator coorelation plots
c = ROOT.TCanvas("c","c",800,800)
histos["fg1_corr"].Draw("colz")
histos["fg1_corr"].GetYaxis().SetTitle("Emul")
histos["fg1_corr"].GetXaxis().SetTitle("Data")
histos["fg1_corr"].SetTitle("Finegrain bit 1 data vs emu for abs(ieta) < 16")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/fg1_corr.png")

c = ROOT.TCanvas("c","c",800,800)
histos["fg2_corr"].Draw("colz")
histos["fg2_corr"].GetYaxis().SetTitle("Emul")
histos["fg2_corr"].GetXaxis().SetTitle("Data")
histos["fg2_corr"].SetTitle("Finegrain bit 2 data vs emu for abs(ieta) < 16")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/fg2_corr.png")

c = ROOT.TCanvas("c","c",800,800)
histos["fg3_corr"].Draw("colz")
histos["fg3_corr"].GetYaxis().SetTitle("Emul")
histos["fg3_corr"].GetXaxis().SetTitle("Data")
histos["fg3_corr"].SetTitle("Finegrain bit 3 data vs emu for abs(ieta) < 16")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/fg3_corr.png")

# ET correlation for specific regions
'''
c = ROOT.TCanvas("c","c",800,800)
histos["et_corr13"].Draw("colz")
histos["et_corr13"].GetYaxis().SetTitle("Emul")
histos["et_corr13"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr13.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr14"].Draw("colz")
histos["et_corr14"].GetYaxis().SetTitle("Emul")
histos["et_corr14"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr14.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr15"].Draw("colz")
histos["et_corr15"].GetYaxis().SetTitle("Emul")
histos["et_corr15"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr15.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr16"].Draw("colz")
histos["et_corr16"].GetYaxis().SetTitle("Emul")
histos["et_corr16"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr16.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr17"].Draw("colz")
histos["et_corr17"].GetYaxis().SetTitle("Emul")
histos["et_corr17"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr17.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr18"].Draw("colz")
histos["et_corr18"].GetYaxis().SetTitle("Emul")
histos["et_corr18"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr18.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr19"].Draw("colz")
histos["et_corr19"].GetYaxis().SetTitle("Emul")
histos["et_corr19"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr19.png")

c = ROOT.TCanvas("c","c",800,800)
histos["et_corr20"].Draw("colz")
histos["et_corr20"].GetYaxis().SetTitle("Emul")
histos["et_corr20"].GetXaxis().SetTitle("Data")
c.SetLogz()
c.SetRightMargin(0.15)
c.SaveAs("test/hists_347746/et_corr20.png")

'''
