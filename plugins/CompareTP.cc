// -*- C++ -*-
//
// Package:    HcalDebug
// Class:      CompareTP
// 
/**\class CompareTP CompareTP.cc HcalDebug/CompareChans/src/CompareTP.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  matthias wolf
//         Created:  Mon Feb 29 13:39:57 CET 2016
// $Id$
//
//


// system include files
#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CalibFormats/CaloTPG/interface/CaloTPGTranscoder.h"
#include "CalibFormats/CaloTPG/interface/CaloTPGRecord.h"
#include "CalibFormats/HcalObjects/interface/HcalDbRecord.h"
#include "CalibFormats/HcalObjects/interface/HcalDbService.h"

#include "CondFormats/DataRecord/interface/HcalChannelQualityRcd.h"
#include "CondFormats/DataRecord/interface/L1CaloGeometryRecord.h"
#include "CondFormats/HcalObjects/interface/HcalChannelQuality.h"
#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"

#include "CondFormats/L1TObjects/interface/L1RCTParameters.h"
#include "CondFormats/DataRecord/interface/L1RCTParametersRcd.h"
#include "CondFormats/L1TObjects/interface/L1CaloHcalScale.h"
#include "CondFormats/DataRecord/interface/L1CaloHcalScaleRcd.h"

#include "DataFormats/Common/interface/SortedCollection.h"
#include "DataFormats/CaloTowers/interface/CaloTower.h"
#include "DataFormats/HcalDigi/interface/HcalDigiCollections.h"
#include "DataFormats/HcalDigi/interface/HcalTriggerPrimitiveDigi.h"
#include "DataFormats/HcalDetId/interface/HcalTrigTowerDetId.h"
#include "DataFormats/HcalDetId/interface/HcalDetId.h"
#include "DataFormats/L1CaloTrigger/interface/L1CaloCollections.h"

#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalGeometry.h"
#include "Geometry/HcalTowerAlgo/interface/HcalTrigTowerGeometry.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"

#include "TH1D.h"
#include "TH2D.h"
#include "TString.h"
#include "TTree.h"
//
// class declaration
//

class CompareTP : public edm::EDAnalyzer {
   public:
      explicit CompareTP(const edm::ParameterSet&);
      ~CompareTP();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void analyze(const edm::Event&, const edm::EventSetup&);

      // ----------member data ---------------------------
      static const int FGCOUNT = 7;

      edm::InputTag digis_;
      edm::InputTag edigis_;

  //      edm::InputTag QIE11_;

      bool swap_iphi_;

      edm::ESGetToken<CaloTPGTranscoder, CaloTPGRecord> tok_hcalCoder_;

      int run_;
      int lumi_;
      int event_;

      TTree *tps_;

      int tp_ieta_;
      int tp_iphi_;
      int tp_depth_;
      int tp_version_;
      int tp_soi_;
      int tp_soi_emul_;
      int tp_soi_soi0_;
      int tp_soi_emul_soi0_;
      int tp_soi_soi1_;
      int tp_soi_emul_soi1_;
      int tp_soi_soi3_;
      int tp_soi_emul_soi3_;
      int tp_npresamples_;
      int tp_npresamples_emul_;
      std::array<int, 10> tp_adc_;
      std::array<int, 10> tp_adc_emul_;
      double tp_et_;
      double tp_et_emul_;
      bool tp_zsMarkAndPass_;
      bool tp_zsMarkAndPass_emul_;
      std::array<int, FGCOUNT> tp_fg_soi0_;
      std::array<int, FGCOUNT> tp_fg_soi1_;
      std::array<int, FGCOUNT> tp_fg_soi_;
      std::array<int, FGCOUNT> tp_fg_soi3_;
      std::array<int, FGCOUNT> tp_fg_emul_soi0_;
      std::array<int, FGCOUNT> tp_fg_emul_soi1_;
      std::array<int, FGCOUNT> tp_fg_emul_soi_;
      std::array<int, FGCOUNT> tp_fg_emul_soi3_;

      int tp_fgs_s0_;
      int tp_fgs_s1_;
      int tp_fgs_s2_;
      int tp_fgs_s3_;
      int tp_fgs_s4_;
      int tp_fgs_emul_s0_;
      int tp_fgs_emul_s1_;
      int tp_fgs_emul_s2_;
      int tp_fgs_emul_s3_;
      int tp_fgs_emul_s4_;

      TH2D *finegrain_vs_event_;
      TH2D *finegrain_emul_vs_event_;
      TH2D *finegrain_vs_event_ieta1_;
      TH2D *finegrain_emul_vs_event_ieta1_;
      TH2D *energy_vs_event_;
      TH2D *energy_emul_vs_event_;
      TH2D *energy_vs_event_ieta1_;
      TH2D *energy_emul_vs_event_ieta1_;
      TH2D *SOIenergy_vs_event_;
      TH2D *SOIenergy_emul_vs_event_;
};

CompareTP::CompareTP(const edm::ParameterSet& config) :
   edm::EDAnalyzer(),
   digis_(config.getParameter<edm::InputTag>("triggerPrimitives")),
   edigis_(config.getParameter<edm::InputTag>("emulTriggerPrimitives")),
   //   QIE11_(config.getParameter<edm::InputTag>("hcalDigiCollectionTag")),
   swap_iphi_(config.getParameter<bool>("swapIphi")),
   tok_hcalCoder_(esConsumes<CaloTPGTranscoder, CaloTPGRecord>())
{
   edm::Service<TFileService> fs;

   consumes<HcalTrigPrimDigiCollection>(digis_);
   consumes<HcalTrigPrimDigiCollection>(edigis_);
   //   consumes<QIE11DigiCollection>(QIE11_);

   finegrain_vs_event_ = fs->make<TH2D>("finegrain_vs_event","Finegrain bits 1-3 in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) vs event number",100,0,10000,15,1,16);
   finegrain_emul_vs_event_ = fs->make<TH2D>("finegrain_emul_vs_event","Finegrain bits 1-3 in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) vs event number",100,0,10000,15,1,16);
   finegrain_vs_event_ieta1_ = fs->make<TH2D>("finegrain_vs_event_ieta1","Finegrain bits 1-3 in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) at ieta=iphi=1 vs event number",100,0,10000,15,1,16);
   finegrain_emul_vs_event_ieta1_ = fs->make<TH2D>("finegrain_emul_vs_event_ieta1","Finegrain bits 1-3 in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) at ieta=iphi=1 vs event number",100,0,10000,15,1,16);
   energy_vs_event_ = fs->make<TH2D>("energy_vs_event","Energy in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) vs event number",100,0,10000,15,1,16);
   energy_emul_vs_event_ = fs->make<TH2D>("energy_emul_vs_event","Energy in SOI-2 to SOI+2 (1-3,4-6,7-9,10-12,13-15) vs event number",100,0,10000,15,1,16);
   energy_vs_event_ieta1_ = fs->make<TH2D>("energy_vs_event_ieta1","Energy in SOI-2 to SOI+1 (1-3,4-6,7-9,10-12) vs event number (ieta1, iphi1)",100,0,10000,15,1,16);
   energy_emul_vs_event_ieta1_ = fs->make<TH2D>("energy_emul_vs_event_ieta1","Energy in SOI-2 to SOI+1 (1-3,4-6,7-9,10-12) vs event number (ieta1, iphi1)",100,0,10000,15,1,16);
   SOIenergy_vs_event_ = fs->make<TH2D>("SOIenergy_vs_event","SOI Energy in vs event number",100,0,10000,256,0,255);
   SOIenergy_emul_vs_event_ = fs->make<TH2D>("SOIenergy_emul_vs_event","SOI Energy in vs event number",100,0,10000,256,0,255);

   tps_ = fs->make<TTree>("tps", "Trigger primitives");
   tps_->Branch("run", &run_);
   tps_->Branch("lumi", &lumi_);
   tps_->Branch("event", &event_);
   tps_->Branch("ieta", &tp_ieta_);
   tps_->Branch("iphi", &tp_iphi_);
   tps_->Branch("depth", &tp_depth_);
   tps_->Branch("version", &tp_version_);
   tps_->Branch("soi", &tp_soi_);
   tps_->Branch("soi_emul", &tp_soi_emul_);
   tps_->Branch("soi_soi0", &tp_soi_soi0_);
   tps_->Branch("soi_emul_soi0", &tp_soi_emul_soi0_);
   tps_->Branch("soi_soi1", &tp_soi_soi1_);
   tps_->Branch("soi_emul_soi1", &tp_soi_emul_soi1_);
   tps_->Branch("soi_soi3", &tp_soi_soi3_);
   tps_->Branch("soi_emul_soi3", &tp_soi_emul_soi3_);
   tps_->Branch("npresamples", &tp_npresamples_);
   tps_->Branch("npresamples_emul", &tp_npresamples_emul_);
   tps_->Branch("et", &tp_et_);
   tps_->Branch("et_emul", &tp_et_emul_);
   tps_->Branch("zsMarkAndPass", &tp_zsMarkAndPass_);
   tps_->Branch("zsMarkAndPass_emul", &tp_zsMarkAndPass_emul_);

   tps_->Branch("fgs_s0", &tp_fgs_s0_);
   tps_->Branch("fgs_s1", &tp_fgs_s1_);
   tps_->Branch("fgs_s2", &tp_fgs_s2_);
   tps_->Branch("fgs_s3", &tp_fgs_s3_);
   tps_->Branch("fgs_s4", &tp_fgs_s4_);
   tps_->Branch("fgs_emul_s0", &tp_fgs_emul_s0_);
   tps_->Branch("fgs_emul_s1", &tp_fgs_emul_s1_);
   tps_->Branch("fgs_emul_s2", &tp_fgs_emul_s2_);
   tps_->Branch("fgs_emul_s3", &tp_fgs_emul_s3_);
   tps_->Branch("fgs_emul_s4", &tp_fgs_emul_s4_);

   for (unsigned int i = 0; i < tp_fg_soi_.size(); ++i)
      tps_->Branch(("fg" + std::to_string(i)).c_str(), &tp_fg_soi_[i]);
   for (unsigned int i = 0; i < tp_fg_soi0_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi0").c_str(), &tp_fg_soi0_[i]);
   for (unsigned int i = 0; i < tp_fg_soi1_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi1").c_str(), &tp_fg_soi1_[i]);
   for (unsigned int i = 0; i < tp_fg_soi3_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi3").c_str(), &tp_fg_soi3_[i]);
   for (unsigned int i = 0; i < tp_fg_emul_soi_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_emul").c_str(), &tp_fg_emul_soi_[i]);
   for (unsigned int i = 0; i < tp_fg_emul_soi0_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi0_emul").c_str(), &tp_fg_emul_soi0_[i]);
   for (unsigned int i = 0; i < tp_fg_emul_soi1_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi1_emul").c_str(), &tp_fg_emul_soi1_[i]);
   for (unsigned int i = 0; i < tp_fg_emul_soi3_.size(); ++i)
     tps_->Branch(("fg" + std::to_string(i) + "_soi3_emul").c_str(), &tp_fg_emul_soi3_[i]);

   for (unsigned int i = 0; i < tp_adc_.size(); ++i)
      tps_->Branch(("adc" + std::to_string(i)).c_str(), (int*) &(tp_adc_[i]));
   for (unsigned int i = 0; i < tp_adc_emul_.size(); ++i)
      tps_->Branch(("adc" + std::to_string(i) + "_emul").c_str(), (int*) &(tp_adc_emul_[i]));
}

CompareTP::~CompareTP() {}

namespace std {
   template<> struct hash<HcalTrigTowerDetId> {
      size_t operator()(const HcalTrigTowerDetId& id) const {
         return hash<int>()(id);
      }
   };
}

void
CompareTP::analyze(const edm::Event& event, const edm::EventSetup& setup)
{
   using namespace edm;

   run_ = event.id().run();
   lumi_ = event.id().luminosityBlock();
   event_ = event.id().event();

   Handle<HcalTrigPrimDigiCollection> digis;
   if (!event.getByLabel(digis_, digis)) {
      LogError("CompareTP") <<
         "Can't find hcal trigger primitive digi collection with tag '" <<
         digis_ << "'" << std::endl;
      return;
   }

   Handle<HcalTrigPrimDigiCollection> edigis;
   if (!event.getByLabel(edigis_, edigis)) {
      LogError("CompareTP") <<
         "Can't find emulated hcal trigger primitive digi collection with tag '" <<
         digis_ << "'" << std::endl;
      return;
   }

   /*   Handle<QIE11DigiCollection> QIE11;
   if (!event.getByLabel(QIE11_,QIE11)) {
     LogError("CompareTP") << 
       "Can't find QIE11 digi collection with tag '" <<
       QIE11_ << "'" << std::endl;
     return;
     } */

   ESHandle<CaloTPGTranscoder> decoder = setup.getHandle(tok_hcalCoder_);

   std::unordered_set<HcalTrigTowerDetId> ids;
   typedef std::unordered_map<HcalTrigTowerDetId, HcalTriggerPrimitiveDigi> digi_map;
   digi_map ds;
   digi_map eds;

   /*   std::unordered_set<HcalDetId> qie_ids;
   typedef std::unordered_map<HcalDetId, QIE11DataFrame> QIE11_map;
   QIE11_map qies; */

   for (const auto& digi: *digis) {
      ids.insert(digi.id());
      ds[digi.id()] = digi;
   }

   for (const auto& digi: *edigis) {
      ids.insert(digi.id());
      eds[digi.id()] = digi;
   }

   /*   for (const auto& digi: *QIE11) {
     qie_ids.insert(digi.detid());
     qies[digi.detid()] = digi;
     }*/

   for (const auto& id: ids) {
      if (id.version() == 1 and abs(id.ieta()) >= 40 and id.iphi() % 4 == 1)
         continue;
      tp_ieta_ = id.ieta();
      tp_iphi_ = id.iphi();
      tp_depth_ = id.depth();
      tp_version_ = id.version();
      digi_map::const_iterator digi;
      if ((digi = ds.find(id)) != ds.end()) {
	//	if (tp_ieta_ == 1 && tp_iphi_ == 1 && ((event.id().event() > 8000 && event.id().event() < 8020) || (event.id().event() > 3000 && event.id().event() < 3020) || (event.id().event() > 6050 && event.id().event() < 6070))) {
	//	if (tp_ieta_ == 1 && tp_iphi_ == 1) { 
	if (tp_ieta_ == 1 && tp_iphi_ == 1 && (event.id().event() == 8000 || event.id().event() == 9149|| event.id().event() == 2050 || event.id().event() == 5608 || event.id().event() == 5609 || event.id().event() == 3031)) {
	  std::cout << "digi->second.sample(TS).compressedEt() energy for TS0 = " << digi->second.sample(0).compressedEt() << ", TS1 = " << digi->second.sample(1).compressedEt() << ", TS2 = SOI = " << digi->second.sample(2).compressedEt() << " = " << digi->second.SOI_compressedEt() << ", TS3 = " << digi->second.sample(3).compressedEt() << std::endl;
	   std::cout << "fine grain bits in TS0 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(0).fineGrain(0) << ", " << digi->second.sample(0).fineGrain(1) << ", " << digi->second.sample(0).fineGrain(2) << ", " << digi->second.sample(0).fineGrain(3) << std::endl;
	   std::cout << "fine grain bits in TS1 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(1).fineGrain(0) << ", " << digi->second.sample(1).fineGrain(1) << ", " << digi->second.sample(1).fineGrain(2) << ", " << digi->second.sample(1).fineGrain(3) << std::endl;
	   std::cout << "fine grain bits in TS2 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(2).fineGrain(0) << ", " << digi->second.sample(2).fineGrain(1) << ", " << digi->second.sample(2).fineGrain(2) << ", " << digi->second.sample(2).fineGrain(3) << std::endl;
	   std::cout << "fine grain bits in TS3 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(3).fineGrain(0) << ", " << digi->second.sample(3).fineGrain(1) << ", " << digi->second.sample(3).fineGrain(2) << ", " << digi->second.sample(3).fineGrain(3) << std::endl;
	   std::cout << "full information for TS2 = SOI is: " << digi->second.sample(2) << ", " << digi->second.t0() << std::endl;
	 }
	 
         tp_soi_ = digi->second.SOI_compressedEt();
         tp_soi_soi0_ = digi->second.sample(0).compressedEt();
         tp_soi_soi1_ = digi->second.sample(1).compressedEt();
         tp_soi_soi3_ = digi->second.sample(3).compressedEt();
         tp_npresamples_ = digi->second.presamples();
         tp_zsMarkAndPass_ = digi->second.zsMarkAndPass();
         tp_et_ = decoder->hcaletValue(id, digi->second.t0());

	 tp_fgs_s0_ = digi->second.sample(0).fineGrain(1) + 2 * digi->second.sample(0).fineGrain(2) + 4 * digi->second.sample(0).fineGrain(3);
	 tp_fgs_s1_ = digi->second.sample(1).fineGrain(1) + 2 * digi->second.sample(1).fineGrain(2) + 4 * digi->second.sample(1).fineGrain(3);
	 tp_fgs_s2_ = digi->second.sample(2).fineGrain(1) + 2 * digi->second.sample(2).fineGrain(2) + 4 * digi->second.sample(2).fineGrain(3);
	 tp_fgs_s3_ = digi->second.sample(3).fineGrain(1) + 2 * digi->second.sample(3).fineGrain(2) + 4 * digi->second.sample(3).fineGrain(3);
	 tp_fgs_s4_ = digi->second.sample(4).fineGrain(1) + 2 * digi->second.sample(4).fineGrain(2) + 4 * digi->second.sample(4).fineGrain(3);
	 
	 if ( abs(id.ieta()) <= 15 ) {
	   for (int SOI = 0; SOI < 5; SOI++) {
	     for (int fgbit = 1; fgbit < 4; fgbit++) {
	       if (digi->second.sample(SOI).fineGrain(fgbit) == 1) {
		 finegrain_vs_event_->Fill(event.id().event(),fgbit + SOI*3);
		 if (id.ieta() == 1 && id.iphi() == 1) finegrain_vs_event_ieta1_->Fill(event.id().event(),fgbit + SOI*3);
	       }
	     }
	     if (digi->second.sample(SOI).compressedEt() > 0) {
	       energy_vs_event_->Fill(event.id().event(),SOI*3 + 1); // 1, 4, 7, 10
	       if (id.ieta() == 1 && id.iphi() == 1) energy_vs_event_ieta1_->Fill(event.id().event(),SOI*3 + 1);
	     }
	   }
	   SOIenergy_vs_event_->Fill(event.id().event(),digi->second.SOI_compressedEt());
	   
	 }
         for (unsigned int i = 0; i < tp_fg_soi_.size(); ++i)
	   tp_fg_soi_[i] = digi->second.t0().fineGrain(i);
	 for (unsigned int i = 0; i < tp_fg_soi0_.size(); ++i)
	   tp_fg_soi0_[i] = digi->second.sample(0).fineGrain(i);
         for (unsigned int i = 0; i < tp_fg_soi1_.size(); ++i)
           tp_fg_soi1_[i] = digi->second.sample(1).fineGrain(i);
         for (unsigned int i = 0; i < tp_fg_soi3_.size(); ++i)
           tp_fg_soi3_[i] = digi->second.sample(3).fineGrain(i);
         for (unsigned int i = 0; i < tp_adc_.size(); ++i)
	   tp_adc_[i] = digi->second[i].compressedEt();
      } else {
	tp_soi_ = 0;
	tp_npresamples_ = 0;
	tp_et_ = 0;
	tp_zsMarkAndPass_ = 0;
	for (unsigned int i = 0; i < tp_fg_soi_.size(); ++i)
	  tp_fg_soi_[i] = 0;
	for (unsigned int i = 0; i < tp_adc_.size(); ++i)
	  tp_adc_[i] = 0;
      }
      auto new_id(id);
      if (swap_iphi_ and id.version() == 1 and id.ieta() > 28 and id.ieta() < 40) {
	if (id.iphi() % 4 == 1)
	  new_id = HcalTrigTowerDetId(id.ieta(), (id.iphi() + 70) % 72, id.depth(), id.version());
	else
	  new_id = HcalTrigTowerDetId(id.ieta(), (id.iphi() + 2) % 72 , id.depth(), id.version());
      }
      if ((digi = eds.find(new_id)) != eds.end()) {
	
        if (tp_ieta_ == 1 && tp_iphi_ == 1 && (event.id().event() == 8000 || event.id().event() == 9149|| event.id().event() == 2050 || event.id().event() == 5608 || event.id().event() == 5609 || event.id().event() == 3031)) {
	  std::cout << "emul digi->second.sample(TS).compressedEt() energy for TS0 = " << digi->second.sample(0).compressedEt() << ", TS1 = " << digi->second.sample(1).compressedEt() << ", TS2 = SOI = " << digi->second.sample(2).compressedEt() << " = " << digi->second.SOI_compressedEt() << ", TS3 = " << digi->second.sample(3).compressedEt() << std::endl;
	  std::cout <<"emul fine grain bits in TS0 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(0).fineGrain(0) << ", " << digi->second.sample(0).fineGrain(1) << ", " << digi->second.sample(0).fineGrain(2) << ", " << digi->second.sample(0).fineGrain(3) << std::endl;
	  std::cout << "emul fine grain bits in TS1 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(1).fineGrain(0) << ", " << digi->second.sample(1).fineGrain(1) << ", " << digi->second.sample(1).fineGrain(2) << ", " << digi->second.sample(1).fineGrain(3) << std::endl;
	  std::cout << "emul fine grain bits in TS2 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(2).fineGrain(0) << ", " << digi->second.sample(2).fineGrain(1) << ", " << digi->second.sample(2).fineGrain(2) << ", " << digi->second.sample(2).fineGrain(3) << std::endl;
	  std::cout << "emul fine grain bits in TS3 = fg0, fg1, fg2, fg3 =  " << digi->second.sample(3).fineGrain(0) << ", " << digi->second.sample(3).fineGrain(1) << ", " << digi->second.sample(3).fineGrain(2) << ", " << digi->second.sample(3).fineGrain(3) << std::endl;
	}
	
	tp_soi_emul_ = digi->second.SOI_compressedEt();
	tp_soi_emul_soi0_ = digi->second.sample(0).compressedEt();
	tp_soi_emul_soi1_ = digi->second.sample(1).compressedEt();
	tp_soi_emul_soi3_ = digi->second.sample(3).compressedEt();
	tp_npresamples_emul_ = digi->second.presamples();
	tp_zsMarkAndPass_emul_ = digi->second.zsMarkAndPass();
	tp_et_emul_ = decoder->hcaletValue(id, digi->second.t0());
	
	tp_fgs_emul_s0_ = digi->second.sample(0).fineGrain(1) + 2 * digi->second.sample(0).fineGrain(2) + 4 * digi->second.sample(0).fineGrain(3);
	tp_fgs_emul_s1_ = digi->second.sample(1).fineGrain(1) + 2 * digi->second.sample(1).fineGrain(2) + 4 * digi->second.sample(1).fineGrain(3);
	tp_fgs_emul_s2_ = digi->second.sample(2).fineGrain(1) + 2 * digi->second.sample(2).fineGrain(2) + 4 * digi->second.sample(2).fineGrain(3);
	tp_fgs_emul_s3_ = digi->second.sample(3).fineGrain(1) + 2 * digi->second.sample(3).fineGrain(2) + 4 * digi->second.sample(3).fineGrain(3);
	tp_fgs_emul_s4_ = digi->second.sample(4).fineGrain(1) + 2 * digi->second.sample(4).fineGrain(2) + 4 * digi->second.sample(4).fineGrain(3);
	
	if ( abs(id.ieta()) <= 15 ) {
	  for (int SOI_emul = 0; SOI_emul < 5; SOI_emul++) {
	    for (int fgbit_emul = 1; fgbit_emul < 4; fgbit_emul++) {
	      if (digi->second.sample(SOI_emul).fineGrain(fgbit_emul) == 1) {
		finegrain_emul_vs_event_->Fill(event.id().event(),fgbit_emul + SOI_emul*3);
		if (id.ieta() == 1 && id.iphi() == 1) finegrain_emul_vs_event_ieta1_->Fill(event.id().event(),fgbit_emul + SOI_emul*3);
	      }
	    }
	    if (digi->second.sample(SOI_emul).compressedEt() > 0) {
	      energy_emul_vs_event_->Fill(event.id().event(),SOI_emul*3 + 1); // 1, 4, 7, 10
	      if (id.ieta() == 1 && id.iphi() == 1) energy_emul_vs_event_ieta1_->Fill(event.id().event(),SOI_emul*3 + 1);
	    }
	  }
	  SOIenergy_emul_vs_event_->Fill(event.id().event(),digi->second.SOI_compressedEt());
	}
	for (unsigned int i = 0; i < tp_fg_emul_soi_.size(); ++i)
	  tp_fg_emul_soi_[i] = digi->second.t0().fineGrain(i);
	for (unsigned int i = 0; i < tp_fg_emul_soi0_.size(); ++i)
	  tp_fg_emul_soi0_[i] = digi->second.sample(0).fineGrain(i);
	for (unsigned int i = 0; i < tp_fg_emul_soi1_.size(); ++i)
	  tp_fg_emul_soi1_[i] = digi->second.sample(1).fineGrain(i);
	for (unsigned int i = 0; i < tp_fg_emul_soi3_.size(); ++i)
	  tp_fg_emul_soi3_[i] = digi->second.sample(3).fineGrain(i);
	for (unsigned int i = 0; i < tp_adc_emul_.size(); ++i)
	  tp_adc_emul_[i] = digi->second[i].compressedEt();
      } else {
	tp_soi_emul_ = 0;
	tp_npresamples_emul_ = 0;
	tp_et_emul_ = 0;
	tp_zsMarkAndPass_emul_ = 0;
	for (unsigned int i = 0; i < tp_fg_emul_soi_.size(); ++i)
	  tp_fg_emul_soi_[i] = 0;
	for (unsigned int i = 0; i < tp_adc_emul_.size(); ++i)
	  tp_adc_emul_[i] = 0;
      }
      tps_->Fill();
   }
}

void
CompareTP::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CompareTP);
