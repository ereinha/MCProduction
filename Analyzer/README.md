# RecHitAnalyzer -- E2E ML Detector Image Producer

The RecHitAnalyzer is a CMSSW `EDAnalyzer` plugin that reads reconstructed detector data from AOD files and produces a ROOT TTree (`RHTree`) containing detector-level "images" for machine learning applications. It maps raw calorimeter and tracker information into spatially organized arrays that preserve detector geometry for neural network training.

## Three Production Paths

The analyzer supports three track modes via the `trackMode` configuration parameter, corresponding to three data generation strategies:

### Path 1: `btvNano` -- PF-trimmed tracks only

Fills only PF candidate-based track branches (`EndTracks*`, `Muons*`).
Tracks are filtered through the Particle Flow algorithm, which applies quality
and resolution cuts -- low-resolution or poorly reconstructed tracks that fail PF
linking are dropped. This gives the same track content as BTVNanoAOD but in the
RecHitAnalyzer detector-image format.

- **Track branches**: `EndTracksPt_EB`, `EndTracksQPt_EB`, `ECAL_EndtracksPt`, `ECAL_muonsPt`, etc.
- **Calorimeter/jet/scalar branches**: All filled as usual
- **General tracks / tracker rechits / triplets / layers**: Skipped
- **Input**: Standard AOD (no extra collections required)
- **Config**: `ConfFile_btvNano_cfg.py`

### Path 2: `fullTracks` -- Untrimmed tracks (no PF filtering)

Fills both PF candidate branches AND `generalTracks`-based branches.
The `generalTracks` collection includes all high-purity reconstructed tracks,
including those that did not pass PF quality/resolution cuts. This is the
"BTVNano equivalent without PF trimming" -- you get the full track 4-momenta
without the Particle Flow selection bias.

- **Track branches**: All PF branches (as in `btvNano`) PLUS `TracksPt_EB`, `TracksQPt_EB`, `ECAL_tracksPt`, etc.
- **Calorimeter/jet/scalar branches**: All filled as usual
- **Tracker rechits / triplets / layers**: Skipped
- **Input**: AOD with extra collections (`generalTracks` must be kept)
- **Config**: `ConfFile_fullTracks_cfg.py`

### Path 3: `all` -- Complete detector images (default)

Fills everything: calorimeter rechits, PF candidates, general tracks, silicon
pixel/strip rechits, track triplets, tracker layer maps, and jet hit masks.
This is the most detailed mode, used for the H->AA->2tau+2photon analysis and
other channels requiring complete low-level detector information.

- **All branches**: Filled
- **Input**: AOD with extra collections (must include `generalTracks`, `siPixelRecHits`, `siStripMatchedRecHits`, etc.)
- **Config**: `ConfFile_cfg.py` (default)

## Collections consumed by the Analyzer

| Collection | InputTag | Used in mode |
|---|---|---|
| ECAL Barrel RecHits | `reducedEcalRecHitsEB` | all three |
| ECAL Endcap RecHits | `reducedEcalRecHitsEE` | all three |
| HCAL HB/HE RecHits | `hbhereco` | all three |
| Gen particles | `genParticles` | all three (MC only) |
| Reco photons | `gedPhotons` | all three |
| AK4 PF jets | `ak4PFJets` | all three |
| AK8 PF jets | `ak8PFJets` | all three |
| AK4 gen jets | `ak4GenJets` | all three |
| PF candidates | `particleFlow` | all three |
| PF MET | `pfMet` | all three |
| Primary vertices | `offlinePrimaryVertices` | all three |
| Secondary vertices | `inclusiveCandidateSecondaryVertices` | all three |
| B-tag discriminators | `pfCombinedInclusiveSecondaryVertexV2BJetTags` | all three |
| IP tag info | `pfImpactParameterTagInfos` | all three |
| General tracks | `generalTracks` | `fullTracks`, `all` |
| Si pixel rechits | `siPixelRecHits` | `all` only |
| Si strip matched rechits | `siStripMatchedRecHits:matchedRecHit` | `all` only |
| Si strip rphi rechits | `siStripMatchedRecHits:rphiRecHit` | `all` only |
| Si strip stereo rechits | `siStripMatchedRecHits:stereoRecHit` | `all` only |
| Electrons | `gedGsfElectrons` | all three |
| Taus | `hpsPFTauProducer` | all three |
| Trigger results | `TriggerResults::HLT` | all three |

## Output TTree branches

### Calorimeter images (all modes)
- `EB_energy`, `EB_time` -- ECAL Barrel
- `EE_energy`, `EE_time` -- ECAL Endcap
- `HBHE_energy`, `HBHE_depth` -- HCAL
- `ECALstitched_*`, `ECALatHCAL_*`, `HCALatEBEE_*` -- coordinate-projected images

### Per-jet constituents for ParT training (`btvNano` and `fullTracks` modes)

These branches mirror the BTVNanoAOD `Jet` + `JetPFCands` + `PFCands` table structure
used by weaver/ParT training pipelines. Constituents are associated to jets via `jetIdx`.

**Jet-level** (one entry per selected jet):
- `Jet_pt`, `Jet_eta`, `Jet_phi`, `Jet_energy`, `Jet_mass` -- jet kinematics
- `Jet_nConstituents` -- number of PF constituents
- `Jet_algo` -- 4 for AK4, 8 for AK8

**PF constituents** (one entry per jet-constituent pair, `btvNano` and `fullTracks`):
- `JetPFCands_jetIdx` -- index into the Jet arrays (links constituent to its jet)
- `JetPFCands_pt`, `_eta`, `_phi`, `_energy`, `_mass` -- PF candidate kinematics
- `JetPFCands_pdgId`, `_charge` -- particle identification
- `JetPFCands_d0`, `_d0Err`, `_dz`, `_dzErr` -- track impact parameters (0 for neutrals)
- `JetPFCands_trkPt`, `_trkEta`, `_trkPhi` -- underlying track kinematics
- `JetPFCands_trkChi2`, `_nHits`, `_nPixelHits` -- track quality
- `JetPFCands_puppiWeight` -- PUPPI weight (1.0 at AOD level)

**General tracks in jet cone** (one entry per jet-track pair, `fullTracks` only):
- `JetTracks_jetIdx` -- index into the Jet arrays
- `JetTracks_pt`, `_eta`, `_phi`, `_energy` -- track kinematics (pion mass assumed)
- `JetTracks_charge`, `_d0`, `_d0Err`, `_dz`, `_dzErr` -- charge and impact parameters
- `JetTracks_chi2`, `_ndof`, `_nHits`, `_nPixelHits`, `_quality` -- track quality

The `JetTracks` table includes ALL high-purity `generalTracks` within the jet cone
(dR < 0.4 for AK4, dR < 0.8 for AK8), including tracks that were not linked by
Particle Flow. This is the key difference from `btvNano` mode.

### PF candidate track images (all modes)
- `EndTracksPt_EB/EE`, `EndTracksQPt_EB/EE` -- PF track pT/charge*pT at EB/EE
- `ECAL_EndtracksPt`, `ECAL_EndtracksQPt` -- PF tracks on stitched ECAL
- `MuonsPt_*`, `MuonsQPt_*` -- PF muon tracks
- `_PV` / `_nPV` variants -- split by primary vertex association

### General track images (`fullTracks` and `all` modes)
- `TracksPt_EB/EE`, `TracksQPt_EB/EE` -- general track pT at EB/EE
- `ECAL_tracksPt`, `ECAL_tracksQPt` -- general tracks on stitched ECAL
- `Tracksd0_PV_*`, `Tracksz0_PV_*` -- impact parameters
- `_PV` / `_nPV` variants

### Tracker rechits, triplets, layers (`all` mode only)
- `TRKlayersAtECALstitched_*` -- tracker layer images
- `TRKTriplets_*` -- track triplet information
- `TrackTripletsAtECAL_*` -- track triplets projected to ECAL

### Event-level info (all modes)
- `JetInfoAtECALstitched_*` -- jet kinematic info
- `ScalarInfo_*` -- event-level quantities
- `JetHitMask_*` -- jet cone hit masks (if enabled)

### Event selection branches (task-dependent)
- `A_diphoton_gen_*`, `A_diphoton_reco_*`, `A_ditau_gen_*` -- for `h2aa2ditau_dipho` task

## Setup

```bash
export SCRAM_ARCH=el8_amd64_gcc11
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd CMSSW_13_0_13/src
eval `scram runtime -sh`
cmsenv

# Required dependencies
git clone https://github.com/svfit/ClassicSVfit TauAnalysis/ClassicSVfit -b fastMTT_21_06_2018
git clone https://github.com/svfit/SVfitTF TauAnalysis/SVfitTF

# Clone the analyzer
git clone git@github.com:ereinha/Analyzer.git

scram b -j 16
cd Analyzer
```

## Running locally

```bash
# Path 3 (all) -- default, requires AOD with extra collections
python3 runRHAnalyzer.py

# Or directly with cmsRun:
cmsRun RecHitAnalyzer/python/ConfFile_cfg.py \
  inputFiles=file:AOD_extra_collection.root \
  maxEvents=100 \
  outputFile=output_all.root

# Path 1 (btvNano) -- PF-trimmed tracks, works on standard AOD
cmsRun RecHitAnalyzer/python/ConfFile_btvNano_cfg.py \
  inputFiles=file:AOD.root \
  maxEvents=100 \
  outputFile=output_btvNano.root

# Path 2 (fullTracks) -- untrimmed tracks, requires AOD with extra collections
cmsRun RecHitAnalyzer/python/ConfFile_fullTracks_cfg.py \
  inputFiles=file:AOD_extra_collection.root \
  maxEvents=100 \
  outputFile=output_fullTracks.root
```

## Running on CRAB

Three CRAB configs are provided:

| Path | CRAB config | Input dataset |
|---|---|---|
| `btvNano` | `crabConfig_RHAnalyzer_HToAATo2Tau2Photon_btvNano.py` | Standard AOD |
| `fullTracks` | `crabConfig_RHAnalyzer_HToAATo2Tau2Photon_fullTracks.py` | AOD with extra collections |
| `all` | `crabConfig_RHAnalyzer_HToAATo2Tau2Photon.py` | AOD with extra collections |

Submit with:
```bash
crab submit -c crabConfig_RHAnalyzer_HToAATo2Tau2Photon.py
```

## Upstream pipeline

The RecHitAnalyzer consumes AOD files produced by the E2E pipeline in
`E2E-HToAATo2Tau2Photon/`:

```
GEN-SIM  -->  HLT+Pileup  -->  AOD (extra collections)  -->  RecHitAnalyzer
                                 |
                                 +--> MiniAOD  -->  NanoAOD (extra collections)
                                 |
                                 +--> MiniAOD  -->  BTVNanoAOD (PF-trimmed)
```

For the `btvNano` path, standard AOD output (without extra collections) is sufficient.
For `fullTracks` and `all` paths, use `AOD_HToAATo2Tau2Photon_extra_collection_cfg.py`
which keeps `generalTracks`, `siPixelRecHits`, `siStripMatchedRecHits`, etc.

## ParT training compatibility

The `btvNano` and `fullTracks` modes produce per-jet constituent data structured
to match the BTVNanoAOD `JetPFCands` + `PFCands` table format used by the
[weaver](https://github.com/hqucms/weaver-core) / ParticleTransformer training pipeline.

The 17 ParT input features can be derived from the stored branches:

| ParT feature | Derivation from stored branches |
|---|---|
| `part_deta` | `JetPFCands_eta - Jet_eta[JetPFCands_jetIdx]` |
| `part_dphi` | `deltaPhi(JetPFCands_phi, Jet_phi[JetPFCands_jetIdx])` |
| `part_pt_log` | `log(JetPFCands_pt)` |
| `part_e_log` | `log(JetPFCands_energy)` |
| `part_logptrel` | `log(JetPFCands_pt / Jet_pt[JetPFCands_jetIdx])` |
| `part_logerel` | `log(JetPFCands_energy / Jet_energy[JetPFCands_jetIdx])` |
| `part_deltaR` | `sqrt(deta^2 + dphi^2)` |
| `part_charge` | `JetPFCands_charge` |
| `part_isChargedHadron` | `abs(JetPFCands_pdgId) == 211` |
| `part_isNeutralHadron` | `abs(JetPFCands_pdgId) == 130` |
| `part_isPhoton` | `abs(JetPFCands_pdgId) == 22` |
| `part_isElectron` | `abs(JetPFCands_pdgId) == 11` |
| `part_isMuon` | `abs(JetPFCands_pdgId) == 13` |
| `part_d0` | `tanh(JetPFCands_d0)` |
| `part_d0err` | `JetPFCands_d0Err` |
| `part_dz` | `tanh(JetPFCands_dz)` |
| `part_dzerr` | `JetPFCands_dzErr` |

For the `fullTracks` mode, the same features can be computed from the `JetTracks_*`
branches. The `JetTracks` table includes tracks that failed PF linking -- these
tracks have no `pdgId` from PF, so PID features should be set to 0 (unknown).

## Key configuration parameters

| Parameter | Default | Description |
|---|---|---|
| `trackMode` | `"all"` | Track filling mode: `"btvNano"`, `"fullTracks"`, or `"all"` |
| `task` | `"dijet_ditau"` | Event selection task (e.g., `"h2aa2ditau_dipho"`) |
| `mode` | `"JetLevel"` | Processing mode: `"JetLevel"` or `"EventLevel"` |
| `doJetHitMask` | `True` | Store only hits within jet cones |
| `granularityMultiPhi/Eta` | `5` | Tracker image granularity multiplier vs ECAL |
| `minJetPt` | `20.0` | Minimum jet pT for jet-level processing |
| `maxJetEta` | `2.4` | Maximum jet eta for jet-level processing |
| `z0PVCut` | `0.1` | z0 cut for primary vertex association |
