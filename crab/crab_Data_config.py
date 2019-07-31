from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'QCD_MC_PU'
config.General.workArea = 'crab_projects_out'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = '../test/analyze_run3.py'

config.Data.inputDataset = '/RelValQCD_FlatPt_15_3000HS_13/CMSSW_10_6_0_pre4-PU25ns_106X_upgrade2021_realistic_v4-v1/GEN-SIM-DIGI-RAW'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = 4
config.Data.publication = False

# This string is used to construct the output dataset name
#config.Data.outputDatasetTag = 'CRAB3_Analysis_test1'

# These values only make sense for processing data
#    Select input data based on a lumi mask
#config.Data.lumiMask = 'Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'

# Where the output files will be transmitted to
config.Data.outLFNDirBase = '/store/group/dpg_hcal/comm_hcal/gillian/LLP_Run3/HcalAnalysisFrameworkFiles/'
config.Site.storageSite = 'T2_CH_CERN'
