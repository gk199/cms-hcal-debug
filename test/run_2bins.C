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
  treeList = "compareReemulRecoSeverity9/tps_match";

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

  // SetBranchAddress for the varaibles accessed from the input file
  tchain->SetBranchAddress("et", &et);
  tchain->SetBranchAddress("ieta", &ieta);
  tchain->SetBranchAddress("iphi", &iphi);
  tchain->SetBranchAddress("depth_max", &depth_max);
  tchain->SetBranchAddress("depth_start", &depth_start);
  tchain->SetBranchAddress("depth_end", &depth_end);
  tchain->SetBranchAddress("soi", &soi);
  tchain->SetBranchAddress("TP_energy_depth", TP_energy_depth);

  // setup necessary histograms for HCAL Barrel region
  // have histograms for inclusive (all ieta regions), and for each ieta region binned by energy ranges
  TH2F* frac_depth_inc_HB = new TH2F("Energy_Depth_HB", "TP Energy Fraction vs Depth in HB", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HB_0510 = new TH2F("Energy_Depth_HB_0510", "TP Energy Fraction vs Depth in HB 0.5-10 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HB_10 = new TH2F("Energy_Depth_HB_10", "TP Energy Fraction vs Depth in HB 10+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  std::map<int, TH2F*> frac_depth_exl_HB_1; // 0.5<et<=10
  std::map<int, TH2F*> frac_depth_exl_HB_2; // 10<et

  for(int eta=0;eta<_length_ietaHB;eta++)
  {
    frac_depth_exl_HB_1[_ietaHB[eta]] = new TH2F(Form("Fraction_Depth_HB_Abs(eta)%d_1",_ietaHB[eta]), Form("TP Energy fraction HB vs Depth Abs(eta)%d 0.5<et<=10",_ietaHB[eta]),8,-0.5,7.5,60,0,1.2);
    frac_depth_exl_HB_2[_ietaHB[eta]] = new TH2F(Form("Fraction_Depth_HB_Abs(eta)%d_2",_ietaHB[eta]), Form("TP Energy fraction HB vs Depth Abs(eta)%d 10<et",_ietaHB[eta]),8,-0.5,7.5,60,0,1.2);
   }
  TH3F* tp_depth_eta_HB = new TH3F("tp_depth_eta_HB", "Energy distribution within TPs for HB", 16,14.5,30.5,7,0.5,7.5,2000,0,200);


  // setup necessary histograms for HCAL Endcap region
  // have histograms for inclusive (all ieta regions), and for each ieta region binned by energy ranges 
  TH2F* frac_depth_inc_HE = new TH2F("Energy_Depth_HE", "TP Energy Fraction vs Depth in HE", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HE_0510 = new TH2F("Energy_Depth_HE_0510", "TP Energy Fraction vs Depth in HE 0.5-10 GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  TH2F* frac_depth_inc_HE_10 = new TH2F("Energy_Depth_HE_10", "TP Energy Fraction vs Depth in HE 10+ GeV", 8, -0.5, 7.5, 60, 0, 1.2);
  std::map<int, TH2F*> frac_depth_exl_HE_1; // 0.5<et<=10                          
  std::map<int, TH2F*> frac_depth_exl_HE_2; // 10<et        

  for(int eta=0;eta<_length_ietaHE;eta++)
    {
      frac_depth_exl_HE_1[_ietaHE[eta]] = new TH2F(Form("Fraction_Depth_HE_Abs(eta)%d_1",_ietaHE[eta]), Form("TP Energy fraction HE vs Depth Abs(eta)%d 0.5<et<=10",_ietaHE[eta]),8,-0.5,7.5,60,0,1.2);
      frac_depth_exl_HE_2[_ietaHE[eta]] = new TH2F(Form("Fraction_Depth_HE_Abs(eta)%d_2",_ietaHE[eta]), Form("TP Energy fraction HE vs Depth Abs(eta)%d 10<et",_ietaHE[eta]),8,-0.5,7.5,60,0,1.2);
    }
  TH3F* tp_depth_eta_HE = new TH3F("tp_depth_eta_HE", "Energy distribution within TPs for HE", 16,14.5,30.5,7,0.5,7.5,2000,0,200);
 

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
              if (et <= 10 )
                {
		  frac_depth_exl_HB_1[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		  frac_depth_inc_HB_0510->Fill(i,TP_energy_depth[i]/et);
                }
              else if (et > 10 )
                {
                  frac_depth_exl_HB_2[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
                  frac_depth_inc_HB_10->Fill(i,TP_energy_depth[i]/et);
		}
	    }

          //******************************** HCAL Endcap events  ****************************************                                                                                                                                    

	  else if (abs(ieta) > 15 && abs(ieta) < 29 )
	    {          
	      frac_depth_inc_HE->Fill(i,TP_energy_depth[i]/et);
	      tp_depth_eta_HE->Fill(abs(ieta),i,TP_energy_depth[i]/et);
	      
	      // now fill in the individual ieta bins and inclusive histograms with energy binning
	      if (et <= 10 )
		{
                 frac_depth_exl_HE_1[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		 frac_depth_inc_HE_0510->Fill(i,TP_energy_depth[i]/et);
		}
	      else if (et > 10 ) 
		{
		  frac_depth_exl_HE_2[abs(ieta)]->Fill(i, TP_energy_depth[i]/et);
		  frac_depth_inc_HE_10->Fill(i,TP_energy_depth[i]/et);
		}
	    }
	}
    }
  }

  // save all the histograms, for Endcap and Barrel regions
  frac_depth_inc_HE->Write();
  frac_depth_inc_HE_0510->Write();
  frac_depth_inc_HE_10->Write();

  tp_depth_eta_HE->Write();
  for(int eta=0;eta<_length_ietaHE;eta++)
  {
    frac_depth_exl_HE_1[_ietaHE[eta]]->Write();
    frac_depth_exl_HE_2[_ietaHE[eta]]->Write();
  }
  frac_depth_inc_HB->Write();
  frac_depth_inc_HB_0510->Write();
  frac_depth_inc_HB_10->Write();

  tp_depth_eta_HB->Write();
  for(int eta=0;eta<_length_ietaHB;eta++)
    {
      frac_depth_exl_HB_1[_ietaHB[eta]]->Write();
      frac_depth_exl_HB_2[_ietaHB[eta]]->Write();
    }

  outFile->Close();
  return 1;
}
