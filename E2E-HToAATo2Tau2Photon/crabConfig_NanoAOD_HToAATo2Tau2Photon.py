from CRABClient.UserUtilities import config
config = config()

Mass_tag = 'm3p6To8'

inputDataset_ = '/GEN_SIM_HToAATo2Tau2Photon_m3p6To8_m3p6To8/lpcml-HToAATo2TauHad2Photon_m3p6To8_pythia8_MiniAOD-d639958dfa8e672fc82464be0b06406f/USER'


#config.section_('General')
config.General.requestName = 'HToAATo2TauHad2Photon_%s_pythia8_NanoAOD'%Mass_tag
config.General.workArea = 'large_scale_runs'
config.General.transferOutputs = True
config.General.transferLogs = True

config.Data.inputDataset = inputDataset_
# config.Data.inputBlocks =inputProcess_
#config.section_('JobType')
#config.JobType.pluginName = 'PrivateMC'
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'NanoAOD_HToAATo2Tau2Photon_cfg.py'
#config.JobType.maxMemoryMB = 4000
config.JobType.maxMemoryMB = 8500
config.JobType.numCores = 4
# config.JobType.maxJobRuntimeMin = 2750

# config.Data.inputDBS = 'global'
config.Data.inputDBS = 'phys03'
config.JobType.allowUndistributedCMSSW = True
#config.Data.inputDataset = inputProcess_

#config.Data.userInputFiles = open('%s'%inputProcess_).readlines()
#config.Data.splitting = 'EventBased'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob    = 1  # units: as defined by config.Data.splitting
config.Data.totalUnits     = -1 # -1: all inputs. total jobs submitted = totalUnits / unitsPerJob. cap of 10k jobs per submission
config.Data.ignoreLocality = True
config.Site.whitelist = ['T3_US_FNALLPC', 'T2_AT_Vienna', 'T2_BE_IIHE', 'T2_BE_UCL', 'T2_BR_SPRACE', 'T2_BR_UERJ', 'T2_CH_CERN', 'T2_CN_Beijing', 'T2_DE_DESY', 'T2_DE_RWTH', 'T2_EE_Estonia', 'T2_ES_CIEMAT', 'T2_ES_IFCA', 'T2_FI_HIP', 'T2_FR_IPHC', 'T2_GR_Ioannina', 'T2_HU_Budapest', 'T2_IN_TIFR', 'T2_IT_Bari', 'T2_IT_Legnaro', 'T2_IT_Pisa', 'T2_IT_Rome', 'T2_KR_KISTI', 'T2_PK_NCP', 'T2_PL_Cyfronet', 'T2_PT_NCG_Lisbon', 'T2_RU_IHEP', 'T2_TR_METU', 'T2_TW_NCHC', 'T2_UA_KIPT', 'T2_UK_London_Brunel', 'T2_UK_London_IC', 'T2_UK_SGrid_Bristol', 'T2_UK_SGrid_RALPP', 'T2_US_Caltech', 'T2_US_Florida', 'T2_US_MIT', 'T2_US_Nebraska', 'T2_US_Purdue', 'T2_US_UCSD', 'T2_US_Vanderbilt', 'T2_US_Wisconsin' ]
# Output files will be stored in config.Site.storageSite at directory:
config.Data.outLFNDirBase = '/store/group/lpcml/ereinhar/MC_signal'
#config.Site.storageSite = 'T2_CH_CERN'
config.Site.storageSite = 'T3_US_FNALLPC'
config.Data.publication = True
config.Data.outputDatasetTag = config.General.requestName