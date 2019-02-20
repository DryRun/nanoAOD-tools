# Common location for specifying paths to JES/JER files
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.enums import *

base_dir =os.path.expandvars("$CMSSW_BASE/src/PhysicsTools/NanoAODTools/data/jme/")

global_tags = {
	Year.k2016:"Summer16_07Aug2017_V11_MC",
	Year.k2017:"Fall17_17Nov2017_V32_MC",
	Year.k2018:"Autumn18_V3_MC"
}

jet_types = [JetType.kAK4PF, JetType.kAK4PFchs, JetType.kAK4PFPuppi, JetType.kAK8PF, JetType.kAK8PFchs, JetType.kAK8PFPuppi]

jer_input_path = {
	Year.k2016:{},
	Year.k2017:{},
	Year.k2018:{},
}
for jet_type in jet_types:
	jer_input_path[Year.k2016][jet_type] = "{}/Summer16_25nsV1_MC/Summer16_25nsV1_MC_PtResolution_{}.txt".format(base_dir, JetTypeString(jet_type))
	jer_input_path[Year.k2017][jet_type] = "{}/Fall17_V3_MC/Fall17_V3_MC_PtResolution_{}.txt".format(base_dir, JetTypeString(jet_type))
	jer_input_path[Year.k2018][jet_type] = "{}/Fall17_V3_MC/Fall17_V3_MC_PtResolution_{}.txt".format(base_dir, JetTypeString(jet_type))

jer_unc_path = {
	Year.k2016:{},
	Year.k2017:{},
	Year.k2018:{},
}
for jet_type in jet_types:
	jer_unc_path[Year.k2016][jet_type] = "{}/Summer16_25nsV1_MC/Summer16_25nsV1_MC_SF_{}.txt".format(base_dir, JetTypeString(jet_type))
	jer_unc_path[Year.k2017][jet_type] = "{}/Fall17_V3_MC/Fall17_V3_MC_SF_{}.txt".format(base_dir, JetTypeString(jet_type))
	jer_unc_path[Year.k2018][jet_type] = "{}/Fall17_V3_MC/Fall17_V3_MC_SF_{}.txt".format(base_dir, JetTypeString(jet_type))

jes_totalunc_path = {}
for year in [Year.k2016, Year.k2017, Year.k2018]:
	jes_totalunc_path[year] = {}
	for jet_type in jet_types:
		jes_totalunc_path[year][jet_type] = "{}/{}_Uncertainty_{}.txt".format(base_dir, global_tags[year], JetTypeString(jet_type))

jes_unc_sources_path = {}
for year in [Year.k2016, Year.k2017, Year.k2018]:
	jes_unc_sources_path[year] = {}
	for jet_type in jet_types:
		jes_unc_sources_path[year][jet_type] = "{}/{}_UncertaintySources_{}.txt".format(base_dir, global_tags[year], JetTypeString(jet_type))

def GetGlobalTag(year):
	return global_tags[year]

def GetJERInputPath(year, jet_type):
	return jer_input_path[year][jet_type]

def GetJERUncertaintyPath(year, jet_type):
	return jer_unc_path[year][jet_type]

def GetJESUncTotalPath(year, jet_type):
	return jes_totalunc_path[year][jet_type]

def GetJESUncSourcesPath(year, jet_type):
	return jes_unc_sources_path[year][jet_type]
