#include "Analyzer/RecHitAnalyzer/interface/RecHitAnalyzer.h"

#include <algorithm>
#include <cmath>

namespace {
  std::vector<float> vJetHitMask_pt_;
  std::vector<float> vJetHitMask_eta_;
  std::vector<float> vJetHitMask_phi_;
  std::vector<float> vJetHitMask_radius_;
  std::vector<int>   vJetHitMask_algo_;
}

void RecHitAnalyzer::branchesJetHitMask(TTree* tree, edm::Service<TFileService>&)
{
  tree->Branch("jetHitMask_pt", &vJetHitMask_pt_);
  tree->Branch("jetHitMask_eta", &vJetHitMask_eta_);
  tree->Branch("jetHitMask_phi", &vJetHitMask_phi_);
  tree->Branch("jetHitMask_radius", &vJetHitMask_radius_);
  tree->Branch("jetHitMask_algo", &vJetHitMask_algo_);
}

void RecHitAnalyzer::fillJetHitMask(const edm::Event& iEvent, const edm::EventSetup&)
{
  jetHitMaskCones_.clear();
  vJetHitMask_pt_.clear();
  vJetHitMask_eta_.clear();
  vJetHitMask_phi_.clear();
  vJetHitMask_radius_.clear();
  vJetHitMask_algo_.clear();

  if (!doJetHitMask_) return;

  auto addJet = [&](const reco::PFJet& jet, const float radius, const int algo) {
    if (jet.pt() < jetHitMaskMinJetPt_) return;
    if (std::abs(jet.eta()) > jetHitMaskMaxJetEta_) return;
    jetHitMaskCones_.push_back(JetCone{static_cast<float>(jet.pt()),
                                       static_cast<float>(jet.eta()),
                                       static_cast<float>(jet.phi()),
                                       radius,
                                       algo});
  };

  if (jetHitMaskUseAK4_) {
    edm::Handle<reco::PFJetCollection> jets;
    if (iEvent.getByToken(jetCollectionT_, jets) && jets.isValid()) {
      for (auto const& jet : *jets) {
        addJet(jet, static_cast<float>(jetHitMaskConeAK4_), 4);
      }
    }
  }

  if (jetHitMaskUseAK8_) {
    edm::Handle<reco::PFJetCollection> jets;
    if (iEvent.getByToken(ak8JetCollectionT_, jets) && jets.isValid()) {
      for (auto const& jet : *jets) {
        addJet(jet, static_cast<float>(jetHitMaskConeAK8_), 8);
      }
    }
  }

  std::sort(jetHitMaskCones_.begin(), jetHitMaskCones_.end(),
            [](const JetCone& a, const JetCone& b) { return a.pt > b.pt; });

  if (jetHitMaskMaxJets_ > 0 && static_cast<int>(jetHitMaskCones_.size()) > jetHitMaskMaxJets_) {
    jetHitMaskCones_.resize(static_cast<std::size_t>(jetHitMaskMaxJets_));
  }

  vJetHitMask_pt_.reserve(jetHitMaskCones_.size());
  vJetHitMask_eta_.reserve(jetHitMaskCones_.size());
  vJetHitMask_phi_.reserve(jetHitMaskCones_.size());
  vJetHitMask_radius_.reserve(jetHitMaskCones_.size());
  vJetHitMask_algo_.reserve(jetHitMaskCones_.size());

  for (auto const& cone : jetHitMaskCones_) {
    vJetHitMask_pt_.push_back(cone.pt);
    vJetHitMask_eta_.push_back(cone.eta);
    vJetHitMask_phi_.push_back(cone.phi);
    vJetHitMask_radius_.push_back(cone.radius);
    vJetHitMask_algo_.push_back(cone.algo);
  }
}

bool RecHitAnalyzer::passJetHitMask(const float& eta, const float& phi) const
{
  if (!doJetHitMask_) return true;
  for (auto const& cone : jetHitMaskCones_) {
    if (reco::deltaR(eta, phi, cone.eta, cone.phi) <= cone.radius) return true;
  }
  return false;
}

