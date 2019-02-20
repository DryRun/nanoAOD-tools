from enum import Enum

class Year(Enum):
	k2016 = 1
	k2017 = 2
	k2018 = 3

class Source(Enum):
	kMC = 1
	kDATA = 2

class Dataset(Enum):
	kJetHT = 1
	kSingleMuon = 2
	kNone = 3

class JetType(Enum):
	kAK4PF      = 1
	kAK4PFchs   = 2
	kAK4PFPuppi = 3
	kAK8PF      = 4
	kAK8PFchs   = 5
	kAK8PFPuppi = 6

def JetTypeString(jet_type_enum):
	if jet_type_enum == JetType.kAK4PF:
		return "AK4"
	elif jet_type_enum == JetType.kAK4PFchs:
		return "AK4PFchs"
	elif jet_type_enum == JetType.kAK4PFPuppi:
		return "AK4PFPuppi"
	elif jet_type_enum == JetType.kAK8PF:
		return "AK8"
	elif jet_type_enum == JetType.kAK8PFchs:
		return "AK8PFchs"
	elif jet_type_enum == JetType.kAK8PFPuppi:
		return "AK8PFPuppi"

class Shift(Enum):
    kNominal = 0
    kDown = 1
    kUp = 2
