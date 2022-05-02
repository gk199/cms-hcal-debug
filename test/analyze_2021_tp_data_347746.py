"""
Template for analyzing local runs. Can be configured
with script one_run.py
"""
import FWCore.ParameterSet.Config as cms

from Configuration.AlCa.GlobalTag import GlobalTag
from Configuration.StandardSequences.Eras import eras

RUN = '347746'
GT = '112X_dataRun3_HLT_v3'

process = cms.Process('PLOT', eras.Run3)

#process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
# syntax for override of a single condition
#override = 'HcalElectronicsMap_2018_v3.0_data,HcalElectronicsMapRcd,frontier://FrontierProd/CMS_CONDITIONS'
override = ''
process.GlobalTag = GlobalTag(process.GlobalTag, GT, override)

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1)) # -1

process.source = cms.Source(
    "HcalTBSource",
    firstLuminosityBlockForEachRun = cms.untracked.VLuminosityBlockID([]),
    fileNames=cms.untracked.vstring(
        '/store/group/dpg_hcal/comm_hcal/USC/run' + RUN + '/USC_' + RUN + '.root'
    )
)

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.RawToDigi_Data_cff")
process.load("SimCalorimetry.Configuration.hcalDigiSequence_cff")
process.load('CalibCalorimetry.CaloTPG.CaloTPGTranscoder_cfi')
process.load('SimCalorimetry.HcalTrigPrimProducers.hcaltpdigi_cff')

process.TFileService = cms.Service("TFileService",
                                   closeFileFast=cms.untracked.bool(True),
                                   fileName=cms.string('analyze_' + RUN + '.root'))

# LUTGenerationMode = False => use L1TriggerObjects (for data)
# LUTGenerationMode = True => use L1TriggerObjects (for MC; default)
process.HcalTPGCoderULUT.LUTGenerationMode = cms.bool(False)
process.simHcalTriggerPrimitiveDigis.inputLabel = cms.VInputTag("hcalDigis", "hcalDigis")
process.simHcalTriggerPrimitiveDigis.inputUpgradeLabel = cms.VInputTag("hcalDigis", "hcalDigis")
# linear LUTs are used by default
#process.CaloTPGTranscoder.linearLUTs = cms.bool(False)
#process.HcalTPGCoderULUT.linearLUTs = cms.bool(False)

process.hcalDigis.silent = cms.untracked.bool(False)
process.hcalDigis.InputLabel = cms.InputTag("source")
# default is True
#process.hcalDigis.FilterDataQuality = cms.bool(False)
#process.hcalDigis.FEDs = [1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117]


process.analyzeRAW = cms.EDAnalyzer("AnalyzeTP",
                                    triggerPrimitives=cms.InputTag("hcalDigis", "", ""),
                                     # vertices
                                    vtxToken=cms.untracked.VInputTag("offlinePrimaryVertices","","RECO"),
                                    doReco = cms.bool(False),
                                    maxVtx = cms.uint32(100),
                                    threshold = cms.untracked.double(0.5)

)
process.analyzeSIM = cms.EDAnalyzer("AnalyzeTP",
                                    triggerPrimitives=cms.InputTag("simHcalTriggerPrimitiveDigis", "", ""),
                                     # vertices
                                    vtxToken=cms.untracked.VInputTag("offlinePrimaryVertices","","RECO"),
                                    doReco = cms.bool(False),
                                    maxVtx = cms.uint32(100),
                                    threshold = cms.untracked.double(0.5)
)

process.compare = cms.EDAnalyzer("CompareTP",
                                 triggerPrimitives=cms.InputTag("hcalDigis"),
                                 emulTriggerPrimitives=cms.InputTag("simHcalTriggerPrimitiveDigis"),
                                 swapIphi=cms.bool(False),
                                 swapIeta=cms.bool(False))

process.p = cms.Path(
    process.hcalDigis *
    process.simHcalTriggerPrimitiveDigis *
    process.analyzeRAW *
    process.analyzeSIM *
    process.compare)
