#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, gensim
class query_vec(object):
	"""docstring for query_vec"""
	def __init__(self, model, keyword):
		self.model = gensim.models.Word2Vec.load(model)
		self.result = ""
		self.keyword = keyword
	def __iter__(self):
		self.result = self.model.most_similar(self.keyword)
		for i in self.result:
			yield str(i[0]), str(i[1])


if __name__  ==  "__main__":
	if len(sys.argv) < 2:
		#sys.argv[0]是模組名稱喔!
		print("Usage:\n\tpython "+sys.argv[0]+"name of model "+"query_keyword")
		sys.exit(1)#0為正常絃拋出一個例外，可以被捕獲
	
	q = query_vec(sys.argv[1], unicode(sys.argv[2], 'utf-8'))
	with open('queryResult.txt','a') as f:
		for i in q:
			print i
