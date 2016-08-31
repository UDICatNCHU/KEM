#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, gensim
import codecs
class query_vec(object):
	"""docstring for query_vec"""
	def __init__(self, model, keyword):
		self.model = gensim.models.Word2Vec.load(model)
		# load wiki model in
		self.result = ""
		self.keyword = keyword
	def __iter__(self):
		self.result = self.model.most_similar(self.keyword)
		# query similar vocabulary with keyword
		for i in self.result:
			yield i[0], i[1]


if __name__  ==  "__main__":
	if len(sys.argv) < 3:
		#sys.argv[0]是模組名稱喔!
		print("Usage:\n\tpython "+sys.argv[0]+" [name of model] "+"[query_keyword]")
		sys.exit(1)#0為正常絃拋出一個例外，可以被捕獲
	#print unicode(sys.argv[2], 'utf-8')
	q = query_vec(sys.argv[1], unicode(sys.argv[2], 'utf-8'))
	# init a query_vec instance with argv, note that if you query with chinese, need to turn chinese into unicode, and also import __future__ from unicode_literal
	f = codecs.open('result.txt','w', encoding='utf-8')
	# codecs can write file with uft-8, which show chinese character correctly
	for i in q:
		print i[0], i[1]
		f.write(i[0]+' '+ str(i[1]))
		f.write('\n')
