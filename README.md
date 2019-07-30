# Setup

Install with:

    git clone git@github.com:cms-hcal-trigger/cms-hcal-debug.git Debug/HcalDebug
    scram b -j 8

# Examples

## With Workflows from `runTheMatrix.py`

Run with:

    runTheMatrix.py -w upgrade -l 10039
    cmsRun Debug/HcalDebug/test/cmp_legacy.py

Change to the output directory and then analyze the second step:

    cmsDriver.py analyze \
      --conditions auto:phase1_2017_realistic \
      -s RAW2DIGI,DIGI --geometry DB:Extended --era Run2_2017 \
      --customise Debug/HcalDebug/customize.analyze_raw_tp \
      --customise Debug/HcalDebug/customize.analyze_reemul_tp \
      --filein file:step2.root \
      -n 10

## Datasets from DAS

Use as input to the `cmsDriver.py` command:

    cmsDriver.py analyze \
      --conditions auto:phase1_2018_realistic \
      -s RAW2DIGI,DIGI --geometry DB:Extended --era Run2_2018 \
      --customise Debug/HcalDebug/customize.analyze_raw_tp \
      --customise Debug/HcalDebug/customize.analyze_reemul_tp \
      --filein das:/RelValQCD_FlatPt_15_3000HS_13/CMSSW_10_1_0_pre3-101X_upgrade2018_realistic_v3-v1/GEN-SIM-DIGI-RAW \
      -n 1000

## From Data, Using L1T Digis

Using a run with HF FG bit mis-matches between L1T inputs and re-emulation:

    cmsDriver.py analyze \
      --data --conditions auto:run2_data \
      -s RAW2DIGI --geometry DB:Extended --era Run2_2017 \
      --customise Debug/HcalDebug/customize.analyze_l1t_tp \
      --customise Debug/HcalDebug/customize.analyze_raw_tp \
      --customise Debug/HcalDebug/customize.analyze_reemul_tp \
      --customise Debug/HcalDebug/customize.compare_l1t_reemul_tp \
      --customise Debug/HcalDebug/customize.use_data_reemul_tp \
      --filein /store/data/Run2017C/HcalNZS/RAW/v1/000/299/844/00000/AE36B18A-5271-E711-A223-02163E013895.root,/store/data/Run2017C/HcalNZS/RAW/v1/000/299/844/00000/46B78BA1-5271-E711-8820-02163E01A60E.root \
      -n -1

## From Data, Using L1T Digis and comparing with RecHits

As before, but using files that contain primary and secondary input file lists, and
adding TriggerPrimitive to RecHit comparisons:

    cmsDriver.py analyze \
      --data --conditions 100X_dataRun2_HLT_v3 \
      -s RAW2DIGI --geometry DB:Extended --era Run2_2018 \
      --no_output \
      --customise Debug/HcalDebug/customize.analyze_l1t_tp \
      --customise Debug/HcalDebug/customize.analyze_raw_tp \
      --customise Debug/HcalDebug/customize.analyze_reemul_tp \
      --customise Debug/HcalDebug/customize.compare_l1t_reemul_tp \
      --customise Debug/HcalDebug/customize.compare_raw_reco_sev9 \
      --customise Debug/HcalDebug/customize.compare_raw_reco_sev9999 \
      --customise Debug/HcalDebug/customize.use_data_reemul_tp \
      --filein=filelist:JetHTRECO.txt \
      --secondfilein=filelist:JetHT.txt \
      -n 50000

## Analyzing one run (global)

The script `one_run.py` provides a quick way to generate a configuration for the analysis of a single run. To analyze run 312712 of the `HcalNZS` dataset in the `Commissioning2018` run period:

    ./one_run.py -r 312712 -t HcalNZS -p Commissioning2018

This will run a DAS command to find the appropriate files before generating the analysis configuration.

## Analyzing one run (local)

Local runs are based on `HcalTBSource` rather than `PoolSource` input and so cannot currently be analyzed with `cmsDriver.py` commands, but the `one_run.py` script can be used with the `-t local` option provides an alternative:

    ./one_run.py -r 312717 -t local

## Analyzing TPs with depth/timing information

    cmsrel CMSSW_10_3_1 
    cd CMSSW_10_3_1/src 
    cmsenv 
    git cms-init 
    git cms-merge-topic --unsafe georgia14:upgradeTPs-103X 
    git clone git@github.com:cms-hcal-trigger/cms-hcal-debug.git Debug/HcalDebug 

In python/customise.py, compare_tp_reco: replace 'HcalCompareLegacyChains' with 'HcalCompareUpgradeChains'.

    scram b -j 4 

See an example config file in test/analyze_325170.py
There exist now upgradeTPs-104X, upgradeTPs-106X branches rebased in 104X, 106X respectively.  

### Specifics for energy-depth and pulse-shape workflow
Workflow (Gillian Kopp, June 2019):

Working in /afs/cern.ch/work/g/gkopp/HCAL_Trigger/CMSSW_10_6_0/src/Debug/HcalDebug, edit plugins/HcalCompareUpgradeChains.cc (for energy-depth, added branch "tp_energy_depth_[8]" to tps and tpsmatch tree; for pulse shape, added branch "tp_ts_adc_[8]" to tps and tpsmatch tree) and analyze_run3.py (list the MC ROOT files to use - currently set up with QCD and LLP Run 3 MC files). Compile and run with:
    
    scram b -j 4
    cd test
    cmsenv
    source runcrab3.sh
    cmsRun analyze_run3.py

This will output "analyze.root" with TP (tps branch, and tps_match with gen matching information for QCD and LLP). In the "tpsmatch" branch, TPs are only saved if they meet the hard scattering, PDG ID, transverse energy, detector acceptance, and delta R matching between the TP and gen parton (DeltaR < 0.5).  Move to QCD/ or LLP/ directory on EOS (/eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles), depending on input ROOT files.

run.C makes histograms from ntuples resulting from cms-hcal-debug packages (analyze.root from previous file). This is currently set to do mode 1 (energy fraction vs. depth) and looks at the TP tree compareReemulRecoSeverity9/tps. run_2bins.C looks at the TP tree compareReemulRecoSeverity9/tps_match with Gen Matching between TPs and MC samples. run_2bins.C splits into 0.5-10 GeV and 10+ GeV, and is used for LLP analysis. Run this with:

    g++ -o run_2bins run_2bins.C  `root-config --cflags --glibs`
    ./run_2bins /eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins/ /eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/QCD_2bins/output_histograms_QCD_2bins.root 1
    
    g++ -o run_2bins run_2bins.C  `root-config --cflags --glibs`
    ./run_2bins /eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh125_mx50_pl500_ev1000/ /eos/cms/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/LLP_mh125_mx50_pl500_ev1000/output_histograms_mh125_mx50_pl500_ev1000.root 1

This will output "output_histograms_QCD.root" "output_histograms_LLP.root", which is needed for the plotting step.

#### run.C and plotting options
run.C makes histograms from ntuples, and is set to split events into three transverse energy bins (0.5-10 GeV, 10-30 GeV, 30+ GeV). run_2bins.C is similar, but only makes 2 energy bins (0.5-5 GeV, 5+ GeV), and is often used for LLP samples.

plot_simple.py has the paths to QCD and TTbar directories, output files, and mode = 1 set. These are used as inputs to ./run again, and then plot_simple.py creates many plots in /outPlots_fraction. No input arguments are needed - just check that path1, path2, mode, out1, out2 are correct.

plot_QCD_LLP.py, plot_QCD_2LLP.py, and plot_QCD_3LLP.py are set to run over ROOT files with the 2 energy bins. plot_QCD_2LLP.py and plot_QCD_3LLP.py make overlayed inclusive plots resulting from 2 or 3 LLP samples. This is useful for plotting mass and lifetime comparisons, respectively.

    cmsenv
    python plot_simple.py
    
    cmsenv
    python plot_QCD_LLP.py
    
Currently run.C and plot_simple.py are set up for analyzing TPs in the HCAL barrel and endcap region, with the Run 3 HCAL segmentation (up to 4 depth layers in HB, up to 7 in HE).

#### Specifics for pulse-shape workflow
HcalCompareUpgradeChains.cc puts the pulse shape information (digi, 8 time slices) in the trees tps and tpsmatch, as branches tp_ts_adc. To make the histogram plots for this, use run_pulse_shape.C (which splits in 2 energy bins, 0.5-5 GeV, 5+ GeV) and plot_pluse_shape.py. These are run with:
    
    g++ -o run_pulse_shape run_pulse_shape.C  `root-config --cflags --glibs`
    ./run_pulse_shape <path to analyze.root file> <path and name of output histogram>.root 1
    
    cmsenv
    python plot_pulse_shape.py 

plot_pluse_shape.py plots one sample at a time, and splits up the pulse shape plots by ieta region. Plots are made for 0.5-5 GeV, 5+ GeV, and inclusive energy region, and have the average point overlayed on the colz plot. plot_pulse_shape_overlay.py allows for overlaying the average pulse shape from two samples (QCD, LLP).
