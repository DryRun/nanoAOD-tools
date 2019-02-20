from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import clearExtraBranches
import sys, time
import ROOT

from abc import ABCMeta, abstractmethod

def eventLoop(modules, inputFile, outputFile, inputTree, wrappedOutputTree, maxEvents=-1, eventRange=None, progress=(10000,sys.stdout), filterOutput=True): 
	for m in modules: 
		m.beginFile(inputFile, outputFile, inputTree, wrappedOutputTree)

	t0 = time.clock(); tlast = t0; doneEvents = 0; acceptedEvents = 0
	entries = inputTree.entries

	for i in xrange(entries) if eventRange == None else eventRange:
		if maxEvents > 0 and i >= maxEvents-1: break
		e = Event(inputTree,i)
		clearExtraBranches(inputTree)
		doneEvents += 1
		ret = True
		for m in modules: 
			ret = m.analyze(e) 
			if not ret: break
		if ret:
			acceptedEvents += 1
		if (ret or not filterOutput) and wrappedOutputTree != None: 
			wrappedOutputTree.fill()
		if progress:
			if i > 0 and i % progress[0] == 0:
				t1 = time.clock()
				progress[1].write("Processed %8d/%8d entries (elapsed time %7.1fs, curr speed %8.3f kHz, avg speed %8.3f kHz), accepted %8d/%8d events (%5.2f%%)\n" % (
						i,entries, t1-t0, (progress[0]/1000.)/(max(t1-tlast,1e-9)), i/1000./(max(t1-t0,1e-9)), acceptedEvents, doneEvents, acceptedEvents/(0.01*doneEvents)))
				tlast = t1
	for m in modules: 
		m.endFile(inputFile, outputFile, inputTree, wrappedOutputTree)

	return (doneEvents, acceptedEvents, time.clock() - t0)
