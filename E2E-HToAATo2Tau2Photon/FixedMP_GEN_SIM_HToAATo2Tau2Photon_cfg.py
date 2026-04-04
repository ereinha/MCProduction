import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_2023_cff import Run3_2023

# Options (cmsRun ... ma=5.0 nEvents=100 gridpack=/path/to/gridpack.tar.xz)
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')

# Fixed-mass pseudoscalar point (GeV) used only for naming/logging here.
# The mass itself must be encoded in the MadGraph gridpack / param_card.
options.register(
    'ma',
    5.0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.float,
    'Pseudoscalar mass point in GeV (for naming/logging; physics set by gridpack).'
)

options.register(
    'nEvents',
    1,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    'Number of events to generate.'
)

options.register(
    'gridpack',
    '',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    'Path to the MadGraph gridpack tarball (.tar.xz / .tar.gz) used by ExternalLHEProducer.'
)

options.register(
    'gridpackDir',
    '',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    'Directory to search for a gridpack matching this process/mass tag if gridpack= is not set.'
)

options.register(
    'makeCards',
    False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    'If True, create an Inputcards_M<tag>/ folder for this ma using Generate_InputCards_hToaaTo2gamma2tau.py.'
)

options.parseArguments()


def _fallback_mass_tag(m: float) -> str:
    # 3.6 -> 3p6, 8.0 -> 8p0
    s = f"{m:.3f}".rstrip("0").rstrip(".")
    if "." not in s:
        s = f"{s}.0"
    return s.replace(".", "p")


try:
    # Local helper (assumed next to this cfg) used to keep naming consistent.
    from Generate_InputCards_hToaaTo2gamma2tau import mass_tag as _mass_tag  # type: ignore
except Exception:
    _mass_tag = _fallback_mass_tag

MA_TAG = _mass_tag(float(options.ma))


if bool(options.makeCards):
    try:
        from Generate_InputCards_hToaaTo2gamma2tau import main as _make_cards_main  # type: ignore
        _make_cards_main([float(options.ma)])
    except Exception as e:
        raise RuntimeError(
            "Requested makeCards=True, but failed to run Generate_InputCards_hToaaTo2gamma2tau.py. "
            "Check that the template Inputcards_M15/ exists in the working directory."
        ) from e


process = cms.Process('SIM', Run3_2023)

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.GeometrySimDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13p6TeVEarly2023Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(int(options.nEvents)),
    output=cms.optional.untracked.allowed(cms.int32, cms.PSet)
)

# No input file: we generate LHE internally (ExternalLHEProducer) and then hadronize.
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(
    FailPath=cms.untracked.vstring(),
    IgnoreCompletely=cms.untracked.vstring(),
    Rethrow=cms.untracked.vstring(),
    SkipEvent=cms.untracked.vstring(),
    accelerators=cms.untracked.vstring('*'),
    allowUnscheduled=cms.obsolete.untracked.bool,
    canDeleteEarly=cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules=cms.untracked.bool(True),
    dumpOptions=cms.untracked.bool(False),
    emptyRunLumiMode=cms.obsolete.untracked.string,
    eventSetup=cms.untracked.PSet(
        forceNumberOfConcurrentIOVs=cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs=cms.untracked.uint32(0)
    ),
    fileMode=cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun=cms.untracked.bool(False),
    holdsReferencesToDeleteEarly=cms.untracked.VPSet(),
    makeTriggerResults=cms.obsolete.untracked.bool,
    modulesToIgnoreForDeleteEarly=cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks=cms.untracked.uint32(1),
    numberOfConcurrentRuns=cms.untracked.uint32(1),
    numberOfStreams=cms.untracked.uint32(0),
    numberOfThreads=cms.untracked.uint32(8),
    printDependencies=cms.untracked.bool(False),
    sizeOfStackForThreadsInKB=cms.optional.untracked.uint32,
    throwIfIllegalParameter=cms.untracked.bool(True),
    wantSummary=cms.untracked.bool(False)
)

process.configurationMetadata = cms.untracked.PSet(
    annotation=cms.untracked.string(
        f'GEN-SIM via MadGraph5+Pythia8: H->aa->(ta+ta-)(gamma gamma), ma={options.ma}GeV'
    ),
    name=cms.untracked.string('Applications'),
    version=cms.untracked.string('$Revision: 1.0 $')
)

process.RAWSIMoutput = cms.OutputModule(
    "PoolOutputModule",
    SelectEvents=cms.untracked.PSet(SelectEvents=cms.vstring('generation_step')),
    compressionAlgorithm=cms.untracked.string('LZMA'),
    compressionLevel=cms.untracked.int32(1),
    dataset=cms.untracked.PSet(
        dataTier=cms.untracked.string('GEN-SIM'),
        filterName=cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize=cms.untracked.int32(20971520),
    fileName=cms.untracked.string(f'file:GEN_SIM_HToAATo2Tau2Photon_ma{MA_TAG}GeV.root'),
    outputCommands=process.RAWSIMEventContent.outputCommands,
    splitLevel=cms.untracked.int32(0)
)

if hasattr(process, "XMLFromDBSource"):
    process.XMLFromDBSource.label = "Extended"
if hasattr(process, "DDDetectorESProducerFromDB"):
    process.DDDetectorESProducerFromDB.label = "Extended"

process.genstepfilter.triggerConditions = cms.vstring("generation_step")

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '130X_mcRun3_2023_realistic_postBPix_v5', '')


process.genHToAATo2Tau2PhotonFilter = cms.EDFilter(
    "GenHToAATo2Tau2PhotonFilter",
    src=cms.InputTag("genParticles"),
    tauPtCut=cms.double(0.0),
    tauEtaCut=cms.double(2.4),
    phoPtCut=cms.double(12.0),
    phoEtaCut=cms.double(2.5),
    phoDrCut=cms.double(0.0),
    diPhoECut=cms.double(32.0),
    diTauECut=cms.double(0.0),
    nHiggs=cms.int32(1),
)


import os
import glob

_gridpack = str(options.gridpack).strip()
if not _gridpack:
    if str(options.gridpackDir).strip():
        # Try to auto-pick a gridpack based on the conventional process name and ma tag.
        _sub = f"hToaaTo2gamma2tau_ma{MA_TAG}GeV"
        _pattern = os.path.join(str(options.gridpackDir), f"*{_sub}*tar*")
        _matches = sorted(glob.glob(_pattern))
        if len(_matches) == 1:
            _gridpack = _matches[0]
        elif len(_matches) > 1:
            raise RuntimeError(
                f"Multiple gridpacks matched pattern '{_pattern}': {', '.join(_matches)}. "
                "Set gridpack= explicitly."
            )
        else:
            raise RuntimeError(
                f"No gridpack matched pattern '{_pattern}'. "
                "Set gridpack= explicitly or check gridpackDir=."
            )
    else:
        raise RuntimeError(
            "You must provide a MadGraph gridpack via gridpack=<path> or a directory via gridpackDir=<dir>. "
            "Example: cmsRun FixedMP_GEN_SIM_HToAATo2Tau2Photon_MG_cfg.py nEvents=100 ma=5.0 "
            "gridpack=/path/to/...tar.xz"
        )


process.externalLHEProducer = cms.EDProducer(
    "ExternalLHEProducer",
    args=cms.vstring(str(_gridpack)),
    nEvents=cms.untracked.uint32(int(options.nEvents)),
    numberOfParameters=cms.uint32(1),
    outputFile=cms.string('cmsgrid_final.lhe'),
    scriptName=cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)


process.generator = cms.EDFilter(
    "Pythia8HadronizerFilter",
    PythiaParameters=cms.PSet(
        parameterSets=cms.vstring('pythia8CommonSettings', 'pythia8CP5Settings', 'processParameters'),

        # Keep CMS CP5 settings, same as the original cfg
        pythia8CP5Settings=cms.vstring(
            'Tune:pp 14',
            'Tune:ee 7',
            'MultipartonInteractions:ecmPow=0.03344',
            'MultipartonInteractions:bProfile=2',
            'MultipartonInteractions:pT0Ref=1.41',
            'MultipartonInteractions:coreRadius=0.7634',
            'MultipartonInteractions:coreFraction=0.63',
            'ColourReconnection:range=5.176',
            'SigmaTotal:zeroAXB=off',
            'SpaceShower:alphaSorder=2',
            'SpaceShower:alphaSvalue=0.118',
            'SigmaProcess:alphaSvalue=0.118',
            'SigmaProcess:alphaSorder=2',
            'MultipartonInteractions:alphaSvalue=0.118',
            'MultipartonInteractions:alphaSorder=2',
            'TimeShower:alphaSorder=2',
            'TimeShower:alphaSvalue=0.118',
            'SigmaTotal:mode = 0',
            'SigmaTotal:sigmaEl = 22.08',
            'SigmaTotal:sigmaTot = 101.037',
            'PDF:pSet=LHAPDF6:NNPDF31_nnlo_as_0118'
        ),

        pythia8CommonSettings=cms.vstring(
            'Tune:preferLHAPDF = 2',
            'Main:timesAllowErrors = 10000',
            'Check:epTolErr = 0.01',
            # In an LHE workflow, the event scale can be taken from the LHEF if desired.
            # Keep the original cfg default unless you have a strong reason to change it.
            'Beams:setProductionScalesFromLHEF = off',
            'SLHA:minMassSM = 1000.',
            'ParticleDecays:limitTau0 = on',
            'ParticleDecays:tau0Max = 10',
            'ParticleDecays:allowPhotonRadiation = on'
        ),

        processParameters=cms.vstring(
            # MLM jet matching for max1j LO samples (align with the *_MLM_* run_card)
            'JetMatching:setMad = off',
            'JetMatching:scheme = 1',
            'JetMatching:merge = on',
            'JetMatching:jetAlgorithm = 2',
            'JetMatching:etaJetMax = 5.0',
            'JetMatching:coneRadius = 1.0',
            'JetMatching:slowJetPower = 1',
            # qCut should be chosen relative to MadGraph xqcut (run_card). For xqcut=30,
            # a common starting point is qCut ~ 1.3-1.5*xqcut.
            'JetMatching:qCut = 45.0',
            'JetMatching:nQmatch = 4',
            'JetMatching:nJetMax = 1',

            # Force hadronic tau decays only
            '15:onMode      = on',
            '15:offIfAny    = 11 -11 13 -13',
        ),
    ),
    comEnergy=cms.double(13600.0),
    crossSection=cms.untracked.double(1.0),
    filterEfficiency=cms.untracked.double(1.0),
    maxEventsToPrint=cms.untracked.int32(1),
    pythiaHepMCVerbosity=cms.untracked.bool(False),
    pythiaPylistVerbosity=cms.untracked.int32(1),
)


# IMPORTANT:
# In cmsDriver-style configs, ProductionFilterSequence is inserted at the front of *all* paths.
# For external LHE generation, it must include BOTH the ExternalLHEProducer and the hadronizer.
process.ProductionFilterSequence = cms.Sequence(process.externalLHEProducer * process.generator)


process.generation_step = cms.Path(process.pgen + process.genHToAATo2Tau2PhotonFilter)
process.simulation_step = cms.Path(process.psim)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

process.schedule = cms.Schedule(
    process.generation_step,
    process.genfiltersummary_step,
    process.simulation_step,
    process.endjob_step,
    process.RAWSIMoutput_step
)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# Filter all paths with the production filter sequence
for path in process.paths:
    getattr(process, path).insert(0, process.ProductionFilterSequence)

# Monitoring / early delete (kept)
from Configuration.DataProcessing.Utils import addMonitoring
process = addMonitoring(process)

from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
