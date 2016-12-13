# -*- coding: utf-8 -*-
import sys, subprocess, json
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from KCM.KCM import KCM

class KEM(KCM):
	""" A KEM object having api for web to query
	Args:
		filePath: path to ptt json file.

	Returns:
		ptt articles with specific keyword.
	"""
	def __init__(self, num, missionType = 'model', ParentDir = ''):
		super().__init__(num, missionType, ParentDir)
		self.WikiModelDirPath = 'word2vec'

	def setDirPath(func):
		@wraps(func)
		def wrap(self, *args, **kw):
			self.DirPath = self.ParentDir + (self.WikiModelDirPath if self.missionType == 'model' else self.JsonDirPath)
			self.fname_extension = 'model' if self.missionType == 'model' else 'json'
			return func(self, *args, **kw)
		return wrap

	def getTerms(self, model, keyword):
		subprocess.call(['python2', 'KEM/querySoup.py', model, keyword, str(self.queryNum)])
		with open('w2v.tmp', 'r') as f:
			result = json.load(f)			
		return result