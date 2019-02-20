import ROOT
import math, os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.module import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import matchObjectCollection, matchObjectCollectionMultiple
from PhysicsTools.NanoAODTools.postprocessing.framework.enums import *

class jetSmearer(Module):
    def __init__(self, globalTag, jetType = "AK4PFchs", jerInputFileName = "Spring16_25nsV10_MC_PtResolution_AK4PFchs.txt", jerUncertaintyInputFileName = "Spring16_25nsV10_MC_SF_AK4PFchs.txt"):

        #--------------------------------------------------------------------------------------------
        # CV: globalTag and jetType not yet used, as there is no consistent set of txt files for
        #     JES uncertainties and JER scale factors and uncertainties yet
        #--------------------------------------------------------------------------------------------

        # read jet energy resolution (JER) and JER scale factors and uncertainties
        # (the txt files were downloaded from https://github.com/cms-jet/JRDatabase/tree/master/textFiles/Spring16_25nsV10_MC )
        self.jerInputFileName = jerInputFileName
        self.jerUncertaintyInputFileName = jerUncertaintyInputFileName

        self.params_sf_and_uncertainty = ROOT.PyJetParametersWrapper()
        self.params_resolution = ROOT.PyJetParametersWrapper()

        # initialize random number generator
        # (needed for jet pT smearing)
        self.rnd = ROOT.TRandom3(12345)

        # load libraries for accessing JER scale factors and uncertainties from txt files
        for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library.replace("lib", ""))
                ROOT.gSystem.Load(library)

    def beginJob(self):

        # initialize JER scale factors and uncertainties
        # (cf. PhysicsTools/PatUtils/interface/SmearedJetProducerT.h )
        print("Loading jet energy resolutions (JER) from file {}".format(self.jerInputFileName))
        self.jer = ROOT.PyJetResolutionWrapper(self.jerInputFileName)
        print("Loading JER scale factors and uncertainties from file {}".format(self.jerUncertaintyInputFileName))
        self.jerSF_and_Uncertainty = ROOT.PyJetResolutionScaleFactorWrapper(self.jerUncertaintyInputFileName)

    def endJob(self):
        pass

        
    def getSmearedJetPt(self, jet, genJet, rho):
        ( jet_pt_nomVal, jet_pt_jerUpVal, jet_pt_jerDownVal ) = self.getSmearValsPt( jet, genJet, rho )
        return ( jet_pt_nomVal*jet.pt, jet_pt_jerUpVal*jet.pt, jet_pt_jerDownVal*jet.pt )
    
    def getSmearValsPt(self, jetIn, genJetIn, rho):

        if hasattr( jetIn, "p4"):
            jet = jetIn.p4()
        else :
            jet = jetIn
        if hasattr( genJetIn, "p4"):
            genJet = genJetIn.p4()
        else :
            genJet = genJetIn

        #--------------------------------------------------------------------------------------------
        # CV: Smear jet pT to account for measured difference in JER between data and simulation.
        #     The function computes the nominal smeared jet pT simultaneously with the JER up and down shifts,
        #     in order to use the same random number to smear all three (for consistency reasons).
        #
        #     The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h 
        #
        #--------------------------------------------------------------------------------------------

        if not (jet.Perp() > 0.):
            print("WARNING: jet pT = %1.1f !!" % jet.Perp())
            return ( jet.Perp(), jet.Perp(), jet.Perp() )
        
        #--------------------------------------------------------------------------------------------
        # CV: define enums needed to access JER scale factors and uncertainties
        #    (cf. CondFormats/JetMETObjects/interface/JetResolutionObject.h) 
        #--------------------------------------------------------------------------------------------

        self.params_resolution.setJetPt(jet.Perp())
        self.params_resolution.setJetEta(jet.Eta())
        self.params_resolution.setRho(rho)
        jet_pt_resolution = self.jer.getResolution(self.params_resolution)

        jet_pt_sf_and_uncertainty = {}
        for enum_central_or_shift in [ Shift.kNominal, Shift.kUp, Shift.kDown ]:
            self.params_sf_and_uncertainty.setJetEta(jet.Eta())
            jet_pt_sf_and_uncertainty[enum_central_or_shift] = self.jerSF_and_Uncertainty.getScaleFactor(self.params_sf_and_uncertainty, enum_central_or_shift.value)

        smear_vals = {}
        for central_or_shift in [ Shift.kNominal, Shift.kUp, Shift.kDown ]:

            smearFactor = None
            if genJet:
                #
                # Case 1: we have a "good" generator level jet matched to the reconstructed jet
                #
                dPt = jet.Perp() - genJet.Perp()
                smearFactor = 1. + (jet_pt_sf_and_uncertainty[central_or_shift] - 1.)*dPt/jet.Perp()
            elif jet_pt_sf_and_uncertainty[central_or_shift] > 1.:
                #
                # Case 2: we don't have a generator level jet. Smear jet pT using a random Gaussian variation
                #
                sigma = jet_pt_resolution*math.sqrt(jet_pt_sf_and_uncertainty[central_or_shift]**2 - 1.)
                smearFactor = self.rnd.Gaus(1., sigma)
            else:
                #
                # Case 3: we cannot smear this jet, as we don't have a generator level jet and the resolution in data is better than the resolution in the simulation,
                #         so we would need to randomly "unsmear" the jet, which is impossible
                #
                smearFactor = 1.

            # check that smeared jet energy remains positive,
            # as the direction of the jet would change ("flip") otherwise - and this is not what we want
            if (smearFactor*jet.Perp()) < 1.e-2:
                smearFactor = 1.e-2

            smear_vals[central_or_shift] = smearFactor
        
        return ( smear_vals[Shift.kNominal], smear_vals[Shift.kUp], smear_vals[Shift.kDown] )
    


    def getSmearValsM(self, jetIn, genJetIn ):
        if hasattr( jetIn, "p4"):
            jet = jetIn.p4()
        else :
            jet = jetIn
        if hasattr( genJetIn, "p4"):
            genJet = genJetIn.p4()
        else :
            genJet = genJetIn

        
        #--------------------------------------------------------------------------------------------
        # CV: Smear jet m to account for measured difference in JER between data and simulation.
        #     The function computes the nominal smeared jet m simultaneously with the JER up and down shifts,
        #     in order to use the same random number to smear all three (for consistency reasons).
        #
        #     The implementation of this function follows PhysicsTools/PatUtils/interface/SmearedJetProducerT.h 
        #
        #--------------------------------------------------------------------------------------------

        if not (jet.M() > 0.):
            print("WARNING: jet m = %1.1f !!" % jet.M())
            return ( jet.M(), jet.M(), jet.M() )
        
        #--------------------------------------------------------------------------------------------
        # CV: define enums needed to access JER scale factors and uncertainties
        #    (cf. CondFormats/JetMETObjects/interface/JetResolutionObject.h) 
        #Shift.kNominal         = 0
        #Shift.kUp        = 2
        #Shift.kDown      = 1
        #--------------------------------------------------------------------------------------------

        jet_m_sf_and_uncertainty = dict( zip( [Shift.kNominal, Shift.kUp, Shift.kDown], [0.1, 0.2, 0.0] ) )

        # generate random number with flat distribution between 0 and 1
        u = self.rnd.Rndm()

        smear_vals = {}
        for central_or_shift in [ Shift.kNominal, Shift.kUp, Shift.kDown ]:

            smearFactor = None
            if genJetIn != None and genJet:
                #
                # Case 1: we have a "good" generator level jet matched to the reconstructed jet
                #
                dM = jet.M() - genJet.M()
                smearFactor = 1. + (jet_m_sf_and_uncertainty[central_or_shift] - 1.)*dM/jet.M()
            elif jet_m_sf_and_uncertainty[central_or_shift] > 1.:
                #
                # Case 2: we don't have a generator level jet. Smear jet m using a random Gaussian variation
                #
                sigma = jet_m_resolution*math.sqrt(jet_m_sf_and_uncertainty[central_or_shift]**2 - 1.)
                smearFactor = self.rnd.Gaus(1., sigma)
            else:
                #
                # Case 3: we cannot smear this jet, as we don't have a generator level jet and the resolution in data is better than the resolution in the simulation,
                #         so we would need to randomly "unsmear" the jet, which is impossible
                #
                smearFactor = 1.

            # check that smeared jet energy remains positive,
            # as the direction of the jet would change ("flip") otherwise - and this is not what we want
            if (smearFactor*jet.M()) < 1.e-2:
                smearFactor = 1.e-2

            smear_vals[central_or_shift] = smearFactor
        
        return ( smear_vals[Shift.kNominal], smear_vals[Shift.kUp], smear_vals[Shift.kDown] )
    
    def analyze(self, event):
        pass

    def beginFile(self):
        pass

    def endFile(self):
        pass
