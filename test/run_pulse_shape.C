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
// this is specifically designed for creating pulse shape histograms for SOI, SOI+1, SOI+2, SOI+3

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
  treeList = "compareReemulRecoSeverity9/tps";
  //treeList = "compareReemulRecoSeverity9/tps_match";

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

  // setting up definitions for pulse shape studies
  int     _pulseshape[] = {0,1,2,3};
  int     _length_pulseshape = (sizeof(_pulseshape)/sizeof(*_pulseshape));

  // defining variables that are extracted from the analyze.root tps tree
  double  et = 0;
  int     ieta = 0;
  int     iphi = 0;
  int     depth_max = 0;
  int     depth_start = 0;
  int     depth_end = 0;
  int     soi = 0;
  int     event = 0;
  double  TP_energy_depth[8] = {0};
  int     tp_ts_adc[8] = {0};
  //  int  TP_pulse_shape[8] = {0};

  // SetBranchAddress for the varaibles accessed from the input file
  tchain->SetBranchAddress("et", &et);
  tchain->SetBranchAddress("ieta", &ieta);
  tchain->SetBranchAddress("iphi", &iphi);
  tchain->SetBranchAddress("depth_max", &depth_max);
  tchain->SetBranchAddress("depth_start", &depth_start);
  tchain->SetBranchAddress("depth_end", &depth_end);
  tchain->SetBranchAddress("soi", &soi);
  tchain->SetBranchAddress("event", &event);
  tchain->SetBranchAddress("TP_energy_depth", TP_energy_depth);
  tchain->SetBranchAddress("tp_ts_adc", tp_ts_adc);
  //  tchain->SetBranchAddress("TP_pulse_shape", TP_pulse_shape);

  // setup necessary histograms for HCAL Barrel region
  // have histograms for each ieta region binned by energy ranges (cannot sum pluse shapes in ieta, so no inclusive plots)
  std::map<int, TH2F*> pulse_shape_exl_HB_3; // all et
  std::map<int, TH2F*> pulse_shape_exl_HB_1; // 0.5<et<=10   
  std::map<int, TH2F*> pulse_shape_exl_HB_2; // 10<et
  for(int eta=0;eta<_length_ietaHB;eta++)
  {
    pulse_shape_exl_HB_3[_ietaHB[eta]] = new TH2F(Form("Pulse_Shape_HB_Abs(eta)%d_3",_ietaHB[eta]), Form("TP Pulse Shape HB vs SOI, Abs(eta)%d, all et",_ietaHB[eta]),8,-0.5,7.5,100,0.,100.);
    pulse_shape_exl_HB_1[_ietaHB[eta]] = new TH2F(Form("Pulse_Shape_HB_Abs(eta)%d_1",_ietaHB[eta]), Form("TP Pulse Shape HB vs SOI, Abs(eta)%d 0.5<et<=10",_ietaHB[eta]),8,-0.5,7.5,100,0.,100.);
    pulse_shape_exl_HB_2[_ietaHB[eta]] = new TH2F(Form("Pulse_Shape_HB_Abs(eta)%d_2",_ietaHB[eta]), Form("TP Pulse Shape HB vs SOI, Abs(eta)%d 10<et",_ietaHB[eta]),8,-0.5,7.5,100,0.,100.);
   }

  // setup necessary histograms for HCAL Endcap region
  // have histograms for each ieta region binned by energy ranges 
  std::map<int, TH2F*> pulse_shape_exl_HE_3; // all et
  std::map<int, TH2F*> pulse_shape_exl_HE_1; // 0.5<et<=10
  std::map<int, TH2F*> pulse_shape_exl_HE_2; // 10<et
  for(int eta=0;eta<_length_ietaHE;eta++)
  {
    pulse_shape_exl_HE_3[_ietaHE[eta]] = new TH2F(Form("Pulse_Shape_HE_Abs(eta)%d_3",_ietaHE[eta]), Form("TP Pulse Shape HE vs SOI, Abs(eta)%d, all et",_ietaHE[eta]),8,-0.5,7.5,100,0.,100.);
    pulse_shape_exl_HE_1[_ietaHE[eta]] = new TH2F(Form("Pulse_Shape_HE_Abs(eta)%d_1",_ietaHE[eta]), Form("TP Pulse Shape HE vs SOI, Abs(eta)%d 0.5<et<=10",_ietaHE[eta]),8,-0.5,7.5,100,0.,100.);
    pulse_shape_exl_HE_2[_ietaHE[eta]] = new TH2F(Form("Pulse_Shape_HE_Abs(eta)%d_2",_ietaHE[eta]), Form("TP Pulse Shape HE vs SOI, Abs(eta)%d 10<et",_ietaHE[eta]),8,-0.5,7.5,100,0.,100.);
  }

  // going through each entry of the input ntuples file
  long int nentries = tchain->GetEntries();
  std::cout << "The number of entries is: " << nentries << std::endl;

  for (long int i = 0;i<nentries;i++)
  {
    //std::cout << "entry: " << i << std::endl;
    //std::cout << "soi: " << soi << std::endl;
    //std::cout << "ieta: " << ieta << std::endl;
    //std::cout << "energy: " << et << std::endl;

    tchain->GetEntry(i);
    
    if ((10*(i+1))%(nentries/10*10) == 0) std::cout << "Has finished " << (10*(i+1))/(nentries/10*10) << "0%..." << std::endl;
    
    if (soi >= 255 ) continue;
    if (abs(ieta) >= 29 ) continue; // these are events in the HCAL Forward region

    if (et > 0.5)
      //std::cout << "get entry: " << i << std::endl;
      //std::cout << "soi: " << soi << std::endl;
      //std::cout << "ieta: " << ieta << std::endl;
      //std::cout << "energy: " << et << std::endl;
    {
      for(int i=0;i<8;i++)
	// going over each pulse shape time slice (4 time slices for TPs)
	{
	  //******************************** HCAL Barrel events  ****************************************                                                                                                                                         
	  if (abs(ieta) <= 15 )
	    {
	      pulse_shape_exl_HB_3[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);

	      // now fill in the individual ieta bins histograms with energy binning                                                        
	      if (et <= 10 )
                {
		  pulse_shape_exl_HB_1[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);
                }
	      else if (et > 10 )
                {
                  pulse_shape_exl_HB_2[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);
		}
	    }

          //******************************** HCAL Endcap events  ****************************************                                                                                                                                    

	  else if (abs(ieta) > 15 && abs(ieta) < 29 )
	    {          
	      pulse_shape_exl_HE_3[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);
	      
	      // now fill in the individual ieta bins histograms with energy binning
	      if (et <= 10 )
		{
		  pulse_shape_exl_HE_1[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);
		}
	      else if (et > 10 ) 
		{
		  pulse_shape_exl_HE_2[abs(ieta)]->Fill(i, (float)tp_ts_adc[i]);
		}
	    }
	}
    }
  }

  // save all the histograms, for Endcap and Barrel regions
  for(int eta=0;eta<_length_ietaHE;eta++)
  {
    pulse_shape_exl_HE_3[_ietaHE[eta]]->Write();
    pulse_shape_exl_HE_1[_ietaHE[eta]]->Write();
    pulse_shape_exl_HE_2[_ietaHE[eta]]->Write();
  }

  for(int eta=0;eta<_length_ietaHB;eta++)
    {
      pulse_shape_exl_HB_3[_ietaHB[eta]]->Write();
      pulse_shape_exl_HB_1[_ietaHB[eta]]->Write();
      pulse_shape_exl_HB_2[_ietaHB[eta]]->Write();
    }

  outFile->Close();
  return 1;
}
