
#include "Analyzer/RecHitAnalyzer/interface/RecHitAnalyzer.h"

// Per-jet constituent storage for ParT training compatibility
// Mirrors BTVNanoAOD JetPFCands + PFCands table structure:
//   - Flat vectors with jetIdx linking constituents to their parent jet
//   - Individual track-level features (pT, eta, phi, d0, dz, pdgId, charge, ...)
//
// Modes:
//   btvNano:    Only PF constituents of each jet (PF-filtered tracks)
//   fullTracks: PF constituents + all generalTracks within jet cone (no PF filtering)

// Jet-level branches (one entry per jet)
namespace {

std::vector<float> vJet_pt_;
std::vector<float> vJet_eta_;
std::vector<float> vJet_phi_;
std::vector<float> vJet_energy_;
std::vector<float> vJet_mass_;
std::vector<int>   vJet_nConstituents_;
std::vector<int>   vJet_algo_;   // 4=AK4, 8=AK8

// PF constituent branches (one entry per jet-constituent pair)
// Mirrors BTVNanoAOD: JetPFCands_jetIdx + PFCands_*

std::vector<int>   vJetPFCands_jetIdx_;
std::vector<float> vJetPFCands_pt_;
std::vector<float> vJetPFCands_eta_;
std::vector<float> vJetPFCands_phi_;
std::vector<float> vJetPFCands_energy_;
std::vector<float> vJetPFCands_mass_;
std::vector<int>   vJetPFCands_pdgId_;
std::vector<int>   vJetPFCands_charge_;
std::vector<float> vJetPFCands_d0_;
std::vector<float> vJetPFCands_d0Err_;
std::vector<float> vJetPFCands_dz_;
std::vector<float> vJetPFCands_dzErr_;
std::vector<float> vJetPFCands_trkPt_;
std::vector<float> vJetPFCands_trkEta_;
std::vector<float> vJetPFCands_trkPhi_;
std::vector<float> vJetPFCands_trkChi2_;
std::vector<int>   vJetPFCands_nHits_;
std::vector<int>   vJetPFCands_nPixelHits_;
std::vector<float> vJetPFCands_puppiWeight_;

// generalTracks branches for fullTracks mode (one entry per jet-track pair)
// Tracks within jet cone from generalTracks, including those NOT linked by PF

std::vector<int>   vJetTracks_jetIdx_;
std::vector<float> vJetTracks_pt_;
std::vector<float> vJetTracks_eta_;
std::vector<float> vJetTracks_phi_;
std::vector<float> vJetTracks_energy_;
std::vector<int>   vJetTracks_charge_;
std::vector<float> vJetTracks_d0_;
std::vector<float> vJetTracks_d0Err_;
std::vector<float> vJetTracks_dz_;
std::vector<float> vJetTracks_dzErr_;
std::vector<float> vJetTracks_chi2_;
std::vector<int>   vJetTracks_ndof_;
std::vector<int>   vJetTracks_nHits_;
std::vector<int>   vJetTracks_nPixelHits_;
std::vector<int>   vJetTracks_quality_;

} // anonymous namespace


// Initialize branches
void RecHitAnalyzer::branchesJetConstituents( TTree* tree, edm::Service<TFileService>& ) {

  // Jet-level
  tree->Branch("Jet_pt",            &vJet_pt_);
  tree->Branch("Jet_eta",           &vJet_eta_);
  tree->Branch("Jet_phi",           &vJet_phi_);
  tree->Branch("Jet_energy",        &vJet_energy_);
  tree->Branch("Jet_mass",          &vJet_mass_);
  tree->Branch("Jet_nConstituents", &vJet_nConstituents_);
  tree->Branch("Jet_algo",          &vJet_algo_);

  // PF constituents (btvNano and fullTracks modes)
  tree->Branch("JetPFCands_jetIdx",     &vJetPFCands_jetIdx_);
  tree->Branch("JetPFCands_pt",         &vJetPFCands_pt_);
  tree->Branch("JetPFCands_eta",        &vJetPFCands_eta_);
  tree->Branch("JetPFCands_phi",        &vJetPFCands_phi_);
  tree->Branch("JetPFCands_energy",     &vJetPFCands_energy_);
  tree->Branch("JetPFCands_mass",       &vJetPFCands_mass_);
  tree->Branch("JetPFCands_pdgId",      &vJetPFCands_pdgId_);
  tree->Branch("JetPFCands_charge",     &vJetPFCands_charge_);
  tree->Branch("JetPFCands_d0",         &vJetPFCands_d0_);
  tree->Branch("JetPFCands_d0Err",      &vJetPFCands_d0Err_);
  tree->Branch("JetPFCands_dz",         &vJetPFCands_dz_);
  tree->Branch("JetPFCands_dzErr",      &vJetPFCands_dzErr_);
  tree->Branch("JetPFCands_trkPt",      &vJetPFCands_trkPt_);
  tree->Branch("JetPFCands_trkEta",     &vJetPFCands_trkEta_);
  tree->Branch("JetPFCands_trkPhi",     &vJetPFCands_trkPhi_);
  tree->Branch("JetPFCands_trkChi2",    &vJetPFCands_trkChi2_);
  tree->Branch("JetPFCands_nHits",      &vJetPFCands_nHits_);
  tree->Branch("JetPFCands_nPixelHits", &vJetPFCands_nPixelHits_);
  tree->Branch("JetPFCands_puppiWeight",&vJetPFCands_puppiWeight_);

  // generalTracks constituents (fullTracks mode only -- branches
  // are created but left empty in btvNano mode)
  tree->Branch("JetTracks_jetIdx",     &vJetTracks_jetIdx_);
  tree->Branch("JetTracks_pt",         &vJetTracks_pt_);
  tree->Branch("JetTracks_eta",        &vJetTracks_eta_);
  tree->Branch("JetTracks_phi",        &vJetTracks_phi_);
  tree->Branch("JetTracks_energy",     &vJetTracks_energy_);
  tree->Branch("JetTracks_charge",     &vJetTracks_charge_);
  tree->Branch("JetTracks_d0",         &vJetTracks_d0_);
  tree->Branch("JetTracks_d0Err",      &vJetTracks_d0Err_);
  tree->Branch("JetTracks_dz",         &vJetTracks_dz_);
  tree->Branch("JetTracks_dzErr",      &vJetTracks_dzErr_);
  tree->Branch("JetTracks_chi2",       &vJetTracks_chi2_);
  tree->Branch("JetTracks_ndof",       &vJetTracks_ndof_);
  tree->Branch("JetTracks_nHits",      &vJetTracks_nHits_);
  tree->Branch("JetTracks_nPixelHits", &vJetTracks_nPixelHits_);
  tree->Branch("JetTracks_quality",    &vJetTracks_quality_);
}


// Fill per-jet constituents
void RecHitAnalyzer::fillJetConstituents( const edm::Event& iEvent, const edm::EventSetup& iSetup ) {

  // Clear all vectors
  vJet_pt_.clear();
  vJet_eta_.clear();
  vJet_phi_.clear();
  vJet_energy_.clear();
  vJet_mass_.clear();
  vJet_nConstituents_.clear();
  vJet_algo_.clear();

  vJetPFCands_jetIdx_.clear();
  vJetPFCands_pt_.clear();
  vJetPFCands_eta_.clear();
  vJetPFCands_phi_.clear();
  vJetPFCands_energy_.clear();
  vJetPFCands_mass_.clear();
  vJetPFCands_pdgId_.clear();
  vJetPFCands_charge_.clear();
  vJetPFCands_d0_.clear();
  vJetPFCands_d0Err_.clear();
  vJetPFCands_dz_.clear();
  vJetPFCands_dzErr_.clear();
  vJetPFCands_trkPt_.clear();
  vJetPFCands_trkEta_.clear();
  vJetPFCands_trkPhi_.clear();
  vJetPFCands_trkChi2_.clear();
  vJetPFCands_nHits_.clear();
  vJetPFCands_nPixelHits_.clear();
  vJetPFCands_puppiWeight_.clear();

  vJetTracks_jetIdx_.clear();
  vJetTracks_pt_.clear();
  vJetTracks_eta_.clear();
  vJetTracks_phi_.clear();
  vJetTracks_energy_.clear();
  vJetTracks_charge_.clear();
  vJetTracks_d0_.clear();
  vJetTracks_d0Err_.clear();
  vJetTracks_dz_.clear();
  vJetTracks_dzErr_.clear();
  vJetTracks_chi2_.clear();
  vJetTracks_ndof_.clear();
  vJetTracks_nHits_.clear();
  vJetTracks_nPixelHits_.clear();
  vJetTracks_quality_.clear();

  // Get vertex for impact parameters
  edm::Handle<reco::VertexCollection> vertexInfo;
  iEvent.getByToken(vertexCollectionT_, vertexInfo);
  const reco::VertexCollection& vtxs = *vertexInfo;
  const reco::Vertex& pv = vtxs.empty() ? reco::Vertex() : vtxs[0];

  // Get generalTracks for fullTracks mode
  edm::Handle<reco::TrackCollection> tracksH;
  bool hasGeneralTracks = false;
  if ( trackMode_ == "fullTracks" ) {
    hasGeneralTracks = iEvent.getByToken( trackCollectionT_, tracksH );
  }

  int jetIdx = 0;

  // Lambda to process one jet collection (AK4 or AK8)
  auto processJetCollection = [&](edm::EDGetTokenT<reco::PFJetCollection>& token,
                                  float coneRadius, int algo)
  {
    edm::Handle<reco::PFJetCollection> jets;
    if ( !iEvent.getByToken(token, jets) || !jets.isValid() ) return;

    for ( unsigned int iJ = 0; iJ < jets->size(); ++iJ ) {
      const reco::PFJet& jet = jets->at(iJ);

      if ( jet.pt() < jetHitMaskMinJetPt_ ) continue;
      if ( std::abs(jet.eta()) > jetHitMaskMaxJetEta_ ) continue;

      // Store jet-level info
      vJet_pt_.push_back( jet.pt() );
      vJet_eta_.push_back( jet.eta() );
      vJet_phi_.push_back( jet.phi() );
      vJet_energy_.push_back( jet.energy() );
      vJet_mass_.push_back( jet.mass() );
      vJet_nConstituents_.push_back( jet.nConstituents() );
      vJet_algo_.push_back( algo );

      // PF constituents (from jet's own constituent list)
      std::vector<reco::PFCandidatePtr> pfCands = jet.getPFConstituents();
      for ( const auto& pfCand : pfCands ) {
        if ( !pfCand.isAvailable() ) continue;

        vJetPFCands_jetIdx_.push_back( jetIdx );
        vJetPFCands_pt_.push_back( pfCand->pt() );
        vJetPFCands_eta_.push_back( pfCand->eta() );
        vJetPFCands_phi_.push_back( pfCand->phi() );
        vJetPFCands_energy_.push_back( pfCand->energy() );
        vJetPFCands_mass_.push_back( pfCand->mass() );
        vJetPFCands_pdgId_.push_back( pfCand->pdgId() );
        vJetPFCands_charge_.push_back( pfCand->charge() );

        // Track-level info (only available for charged PF candidates)
        const reco::Track* trk = pfCand->bestTrack();
        if ( trk ) {
          float d0  = vtxs.empty() ? trk->dxy() : trk->dxy(pv.position());
          float dz  = vtxs.empty() ? trk->dz()  : trk->dz(pv.position());

          vJetPFCands_d0_.push_back( d0 );
          vJetPFCands_d0Err_.push_back( trk->dxyError() );
          vJetPFCands_dz_.push_back( dz );
          vJetPFCands_dzErr_.push_back( trk->dzError() );
          vJetPFCands_trkPt_.push_back( trk->pt() );
          vJetPFCands_trkEta_.push_back( trk->eta() );
          vJetPFCands_trkPhi_.push_back( trk->phi() );
          vJetPFCands_trkChi2_.push_back( trk->normalizedChi2() );
          vJetPFCands_nHits_.push_back( trk->numberOfValidHits() );
          vJetPFCands_nPixelHits_.push_back( trk->hitPattern().numberOfValidPixelHits() );
        } else {
          // Neutral candidates: fill with defaults
          vJetPFCands_d0_.push_back( 0. );
          vJetPFCands_d0Err_.push_back( 0. );
          vJetPFCands_dz_.push_back( 0. );
          vJetPFCands_dzErr_.push_back( 0. );
          vJetPFCands_trkPt_.push_back( 0. );
          vJetPFCands_trkEta_.push_back( 0. );
          vJetPFCands_trkPhi_.push_back( 0. );
          vJetPFCands_trkChi2_.push_back( 0. );
          vJetPFCands_nHits_.push_back( 0 );
          vJetPFCands_nPixelHits_.push_back( 0 );
        }
        vJetPFCands_puppiWeight_.push_back( 1. ); // Not available at AOD level

      } // PF constituents

      // generalTracks within jet cone (fullTracks mode only)
      if ( trackMode_ == "fullTracks" && hasGeneralTracks && tracksH.isValid() ) {
        reco::Track::TrackQuality tkQt = reco::Track::qualityByName("highPurity");

        for ( reco::TrackCollection::const_iterator iTk = tracksH->begin();
              iTk != tracksH->end(); ++iTk ) {
          if ( !iTk->quality(tkQt) ) continue;

          float dR = reco::deltaR( jet.eta(), jet.phi(), iTk->eta(), iTk->phi() );
          if ( dR > coneRadius ) continue;

          float d0  = vtxs.empty() ? iTk->dxy() : iTk->dxy(pv.position());
          float dz  = vtxs.empty() ? iTk->dz()  : iTk->dz(pv.position());

          // Compute energy assuming pion mass
          float pionMass = 0.13957;
          float p = iTk->p();
          float energy = std::sqrt(p*p + pionMass*pionMass);

          vJetTracks_jetIdx_.push_back( jetIdx );
          vJetTracks_pt_.push_back( iTk->pt() );
          vJetTracks_eta_.push_back( iTk->eta() );
          vJetTracks_phi_.push_back( iTk->phi() );
          vJetTracks_energy_.push_back( energy );
          vJetTracks_charge_.push_back( iTk->charge() );
          vJetTracks_d0_.push_back( d0 );
          vJetTracks_d0Err_.push_back( iTk->dxyError() );
          vJetTracks_dz_.push_back( dz );
          vJetTracks_dzErr_.push_back( iTk->dzError() );
          vJetTracks_chi2_.push_back( iTk->normalizedChi2() );
          vJetTracks_ndof_.push_back( iTk->ndof() );
          vJetTracks_nHits_.push_back( iTk->numberOfValidHits() );
          vJetTracks_nPixelHits_.push_back( iTk->hitPattern().numberOfValidPixelHits() );
          vJetTracks_quality_.push_back( iTk->qualityMask() );

        } // generalTracks
      } // fullTracks mode

      jetIdx++;
    } // jets
  }; // lambda

  // Process AK4 jets
  if ( jetHitMaskUseAK4_ ) {
    processJetCollection( jetCollectionT_, static_cast<float>(jetHitMaskConeAK4_), 4 );
  }

  // Process AK8 jets
  if ( jetHitMaskUseAK8_ ) {
    processJetCollection( ak8JetCollectionT_, static_cast<float>(jetHitMaskConeAK8_), 8 );
  }

  if ( debug ) {
    std::cout << " >> JetConstituents: " << vJet_pt_.size() << " jets, "
              << vJetPFCands_jetIdx_.size() << " PF constituents";
    if ( trackMode_ == "fullTracks" ) {
      std::cout << ", " << vJetTracks_jetIdx_.size() << " general tracks";
    }
    std::cout << std::endl;
  }

} // fillJetConstituents()
