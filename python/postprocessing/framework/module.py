import sys
import ROOT
from abc import ABCMeta, abstractmethod

class Module(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		self._hist_file = None

	@abstractmethod
	def beginJob(self):
		pass

	@abstractmethod
	def endJob(self):
		pass

	def addHistogramFile(self, filename):
		self._hist_file = ROOT.TFile(filename, "RECREATE")

	@abstractmethod			
	def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
		pass

	@abstractmethod
	def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
		pass

	@abstractmethod
	def analyze(self, event):
		"""process event, return True (go to next module) or False (fail, go to next event)"""
		pass

	def addObject(self, obj):
		setattr(self, obj.GetName(), obj)
		self.objs.append(getattr(self, obj.GetName()))

	def addObjectList(self, names, obj):
		objlist = []
		for iname,name in enumerate(names):
			setattr(self, obj.GetName() + '_' + name, obj.Clone(obj.GetName() + '_' + name))
			objlist.append(getattr(self, obj.GetName() + '_' + name))
			self.objs.append(getattr(self, obj.GetName() + '_' + name))
		setattr(self, obj.GetName(), objlist)
