#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <map>
#include <math.h>

#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TH1.h"
#include "TH2.h"
#include "TH3.h"
#include "TProfile.h"
#include "TProfile2D.h"
// to compile:
// g++ -o run run.C  `root-config --cflags --glibs`
// to run:
// ./run /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/____/ output_histograms.root 1
// the first argument is the directory where the output file analyze.root from the HcalCompareUpgradeChains is stored
// the second is the name of the output file with histograms made from this macro

// Edited by: gillian kopp [2019] for TP studies with depth and timing information
// workflow: HcalCompareUpgradeChains.cc and analyze_run3.py, outputs analyze.root. run.C, outputs output_histograms.root, move to FilesToPlot. Then run plot.py
// This version is only for ''mode 1'' meaning energy fraction vs. depth information
// tps is TPs without gen matching, tps_matches is TPs with gen matching (for both QCD and LLP hard scattering processes)

int main(int argc, char* argv[])
{

  // NUMBER OF PARAMETERS
  const int Nparam=3;
  if(argc!=Nparam+1)
  {
     std::cout << "main() : arcg = " << argc << " is different from " << Nparam+1 <<". Exiting." << std::endl;
     std::cout << "Usage  : ./run /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug/test/______/ output_histograms.root 1" << std::endl;
     exit (1);
  }

  std::string inputList(argv[1]);
  std::string _outFile  (argv[2]);
  std::string treeList = "";

  // which tree to look at from the input file, here only looking at Trigger Primatives (TPs)
  //treeList = "compareReemulRecoSeverity9/tps";
  //treeList = "compareReemulRecoSeverity9/tps_match";
  treeList = "compareReemulRecoSeverity9/tps_matchHCAL";
  //treeList = "compareReemulRecoSeverity9/tps_match1";
  //treeList = "compareReemulRecoSeverity9/tps_match2";
  //treeList = "compareReemulRecoSeverity9/tps_match3";
 

  TString dir = TString(inputList.c_str());
  TFile *outFile = new TFile(_outFile.c_str(), "RECREATE");
  TChain *tchain = new TChain(treeList.c_str());

  tchain->Add(dir+"analyze.root");
  // this is the name of the file to run on, it is the output of the hcal-debug packages step

  // setting up the regions for the HCAL Barrel (HB) and HCAL Endcap (HE), both regions will be considered. Defined by ieta ranges
  int     _ietaHB[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
  int     _length_ietaHB = (sizeof(_ietaHB)/sizeof(*_ietaHB));
  int     _depthHB[] ={0,1,2,3,4,5,6,7};
  int     _length_depthHB = (sizeof(_depthHB)/sizeof(*_depthHB));

  int     _ietaHE[] = {16,17,18,19,20,21,22,23,24,25,26,27,28,29};
  int     _length_ietaHE = (sizeof(_ietaHE)/sizeof(*_ietaHE));
  int     _depthHE[] ={0,1,2,3,4,5,6,7};
  int     _length_depthHE = (sizeof(_depthHE)/sizeof(*_depthHE));

  // defining variables that are extracted from the analyze.root tps tree
  double  et = 0;
  int     ieta = 0;
  int     iphi = 0;
  int     depth_max = 0;
  int     depth_start = 0;
  int     depth_end = 0;
  int     soi = 0;
  double  TP_energy_depth[8] = {0};
  double  min_deltaR = 0;
  double  min_deltaR_HCAL = 0;

  // SetBranchAddress for the varaibles accessed from the input file
  tchain->SetBranchAddress("et", &et);
  tchain->SetBranchAddress("ieta", &ieta);
  tchain->SetBranchAddress("iphi", &iphi);
  tchain->SetBranchAddress("depth_max", &depth_max);
  tchain->SetBranchAddress("depth_start", &depth_start);
  tchain->SetBranchAddress("depth_end", &depth_end);
  tchain->SetBranchAddress("soi", &soi);
  tchain->SetBranchAddress("TP_energy_depth", TP_energy_depth);
  //  tchain->SetBranchAddress("min_deltaR", &min_deltaR);
  // this is for if using tree tps_matchHCAL where only events where the LLP decays in the HCAL are saved. Then comment out min_deltaR above.
  tchain->SetBranchAddress("min_deltaR_HCAL", &min_deltaR_HCAL);

  // setup necessary histograms for HCAL Barrel region
  // have histograms for inclusive (all ieta regions), and for each ieta region binned by energy ranges
  TH2F* frac_depth_inc_HB = new TH2F("Energy_Depth_HB", "TP Energy Fraction vs Depth in HB", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HB_055 = new TH2F("Energy_Depth_HB_055", "TP Energy Fraction vs Depth in HB 0.5-5 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HB_5 = new TH2F("Energy_Depth_HB_5", "TP Energy Fraction vs Depth in HB 5+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);

  TH1F* min_deltaR_low = new TH1F("min_deltaR_low", "Min DeltaR, 0.5 - 5 GeV", 100, 0, 0.5);
  TH1F* min_deltaR_high = new TH1F("min_deltaR_high", "Min DeltaR, 5 + GeV", 100, 0, 0.5);
  
  std::map<int, TH2F*> frac_depth_exl_HB_1; // 0.5<et<=5
  std::map<int, TH2F*> frac_depth_exl_HB_2; // 5<et

  for(int eta=0;eta<_length_ietaHB;eta++)
  {
    frac_depth_exl_HB_1[_ietaHB[eta]] = new TH2F(Form("Fraction_Depth_HB_Abs(eta)%d_1",_ietaHB[eta]), Form("TP Energy fraction HB vs Depth Abs(eta)%d 0.5<et<=5",_ietaHB[eta]),8,-0.5,7.5,60,0,1.2);
    frac_depth_exl_HB_2[_ietaHB[eta]] = new TH2F(Form("Fraction_Depth_HB_Abs(eta)%d_2",_ietaHB[eta]), Form("TP Energy fraction HB vs Depth Abs(eta)%d 5<et",_ietaHB[eta]),8,-0.5,7.5,60,0,1.2);
   }
  TH3F* tp_depth_eta_HB = new TH3F("tp_depth_eta_HB", "Energy distribution within TPs for HB", 16,14.5,30.5,7,0.5,7.5,2000,0,200);


  // setup necessary histograms for HCAL Endcap region
  // these are both HE ieta inclusive, and broken up 17-21 ieta, 22-28 ieta as this is where tower size increases
  // have histograms for inclusive (all ieta regions), and for each ieta region binned by energy ranges 
  TH2F* frac_depth_inc_HE = new TH2F("Energy_Depth_HE", "TP Energy Fraction vs Depth in HE", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HE_055 = new TH2F("Energy_Depth_HE_055", "TP Energy Fraction vs Depth in HE 0.5-5 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HE_5 = new TH2F("Energy_Depth_HE_5", "TP Energy Fraction vs Depth in HE 5+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);

  TH2F* frac_depth_inc_17_21_HE = new TH2F("Energy_Depth_17_21_HE", "TP Energy Fraction vs Depth in HE, ieta 17-21", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_17_21_HE_055 = new TH2F("Energy_Depth_17_21_HE_055", "TP Energy Fraction vs Depth in HE, ieta 17-21, 0.5-5 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_17_21_HE_5 = new TH2F("Energy_Depth_17_21_HE_5", "TP Energy Fraction vs Depth in HE, ieta 17-21, 5+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);

  TH2F* frac_depth_inc_22_28_HE = new TH2F("Energy_Depth_22_28_HE", "TP Energy Fraction vs Depth in HE, ieta 22-28", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_22_28_HE_055 = new TH2F("Energy_Depth_22_28_HE_055", "TP Energy Fraction vs Depth in HE, ieta 22-28, 0.5-5 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_22_28_HE_5 = new TH2F("Energy_Depth_22_28_HE_5", "TP Energy Fraction vs Depth in HE, ieta 22-28, 5+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);

  std::map<int, TH2F*> frac_depth_exl_HE_1; // 0.5<et<=5  
  std::map<int, TH2F*> frac_depth_exl_HE_2; // 5<et        


  for(int eta=0;eta<_length_ietaHE;eta++)
    {
      frac_depth_exl_HE_1[_ietaHE[eta]] = new TH2F(Form("Fraction_Depth_HE_Abs(eta)%d_1",_ietaHE[eta]), Form("TP Energy fraction HE vs Depth Abs(eta)%d 0.5<et<=5",_ietaHE[eta]),8,-0.5,7.5,60,0,1.2);
      frac_depth_exl_HE_2[_ietaHE[eta]] = new TH2F(Form("Fraction_Depth_HE_Abs(eta)%d_2",_ietaHE[eta]), Form("TP Energy fraction HE vs Depth Abs(eta)%d 5<et",_ietaHE[eta]),8,-0.5,7.5,60,0,1.2);
    }
  TH3F* tp_depth_eta_HE = new TH3F("tp_depth_eta_HE", "Energy distribution within TPs for HE", 16,14.5,30.5,7,0.5,7.5,2000,0,200);
  TH3F* tp_depth_eta_17_21_HE = new TH3F("tp_depth_eta_17_21_HE", "Energy distribution within TPs for HE, ieta 17-21", 16,14.5,30.5,7,0.5,7.5,2000,0,200);
  TH3F* tp_depth_eta_22_28_HE = new TH3F("tp_depth_eta_22_28_HE", "Energy distribution within TPs for HE, ieta 22-28", 16,14.5,30.5,7,0.5,7.5,2000,0,200);

  // going through each entry of the input ntuples file
  long int nentries = tchain->GetEntries();
  std::cout << "The number of entries is: " << nentries << std::endl;

  for (long int i = 0;i<nentries;i++)
  {
    tchain->GetEntry(i);
    if ((10*(i+1))%(nentries/10*10) == 0) std::cout << "Has finished " << (10*(i+1))/(nentries/10*10) << "0%..." << std::endl;
    
    if (soi >= 255 ) continue;
    if (abs(ieta) >= 29 ) continue; // these are events in the HCAL Forward region
    if (et > 0.5)

    {
      for(int i=0;i<8;i++)
	// going over each depth level
	{
	  //******************************** HCAL Barrel events  ****************************************                                                                                                                                         
	  if (abs(ieta) <= 15 )
	    {
              frac_depth_inc_HB->Fill(i,TP_energy_depth[i]/et);
              tp_depth_eta_HB->Fill(abs(ieta),i,TP_energy_depth[i]/et);

	      // now fill in the individual ieta bins and inclusive histograms with energy binning                                                                                       
              if (et <= 5 )
                {
		  frac_depth_exl_HB_1[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		  frac_depth_inc_HB_055->Fill(i,TP_energy_depth[i]/et);
		  min_deltaR_low->Fill(min_deltaR_HCAL);
                }
              else if (et > 5 )
                {
                  frac_depth_exl_HB_2[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
                  frac_depth_inc_HB_5->Fill(i,TP_energy_depth[i]/et);
		  min_deltaR_high->Fill(min_deltaR_HCAL);
		}
	    }

          //******************************** HCAL Endcap events  ****************************************                                                                                                                                    

	  else if (abs(ieta) > 15 && abs(ieta) < 29 )
	    {          
	      frac_depth_inc_HE->Fill(i,TP_energy_depth[i]/et);
	      tp_depth_eta_HE->Fill(abs(ieta),i,TP_energy_depth[i]/et);
	      
	      // now fill in the individual ieta bins and inclusive histograms with energy binning
	      if (et <= 5 )
		{
                 frac_depth_exl_HE_1[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		 frac_depth_inc_HE_055->Fill(i,TP_energy_depth[i]/et);
		 min_deltaR_low->Fill(min_deltaR_HCAL);
		}
	      else if (et > 5 ) 
		{
		  frac_depth_exl_HE_2[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		  frac_depth_inc_HE_5->Fill(i,TP_energy_depth[i]/et);
		  min_deltaR_high->Fill(min_deltaR_HCAL);
		}

	      // fill HE ieta 17-21 inclusive plots
	      if (abs(ieta) < 22 ) 
		{
		  frac_depth_inc_17_21_HE->Fill(i, TP_energy_depth[i]/et);
		  tp_depth_eta_17_21_HE->Fill(abs(ieta),i,TP_energy_depth[i]/et);
		  // now also fill with energy binning
		  if (et <= 5 )
		    {
		      frac_depth_inc_17_21_HE_055->Fill(i, TP_energy_depth[i]/et);
		    }
		  else if (et > 5 )
		    {
		      frac_depth_inc_17_21_HE_5->Fill(i, TP_energy_depth[i]/et);
		    }
		}

	      // fill HE ieta 22-28 inclusive plots (this is after tower size increases, phi segmentation is now 10 degrees)
	      else if (abs(ieta) >= 22 )
		{
		  frac_depth_inc_22_28_HE->Fill(i, TP_energy_depth[i]/et);
                  tp_depth_eta_22_28_HE->Fill(abs(ieta),i,TP_energy_depth[i]/et);
		  // now also fill with energy binning
		  if (et <= 5 )
		    {
		      frac_depth_inc_22_28_HE_055->Fill(i, TP_energy_depth[i]/et);
		    }
		  else if (et > 5 )
		    {
		      frac_depth_inc_22_28_HE_5->Fill(i, TP_energy_depth[i]/et);
		    }
		}
	    }
	}
    }
  }

  // save all the histograms, for Endcap and Barrel regions
  frac_depth_inc_HE->Write();
  frac_depth_inc_HE_055->Write();
  frac_depth_inc_HE_5->Write();

  frac_depth_inc_17_21_HE->Write();
  frac_depth_inc_17_21_HE_055->Write();
  frac_depth_inc_17_21_HE_5->Write();

  frac_depth_inc_22_28_HE->Write();
  frac_depth_inc_22_28_HE_055->Write();
  frac_depth_inc_22_28_HE_5->Write();

  min_deltaR_low->Write();
  min_deltaR_high->Write();

  tp_depth_eta_HE->Write();
  tp_depth_eta_17_21_HE->Write();
  tp_depth_eta_22_28_HE->Write();

  for(int eta=0;eta<_length_ietaHE;eta++)
  {
    frac_depth_exl_HE_1[_ietaHE[eta]]->Write();
    frac_depth_exl_HE_2[_ietaHE[eta]]->Write();
  }
  frac_depth_inc_HB->Write();
  frac_depth_inc_HB_055->Write();
  frac_depth_inc_HB_5->Write();

  tp_depth_eta_HB->Write();

  for(int eta=0;eta<_length_ietaHB;eta++)
    {
      frac_depth_exl_HB_1[_ietaHB[eta]]->Write();
      frac_depth_exl_HB_2[_ietaHB[eta]]->Write();
    }

  outFile->Close();
  return 1;
}
