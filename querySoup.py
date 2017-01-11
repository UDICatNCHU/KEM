#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, gensim
import codecs, json
class query_vec(object):
    """docstring for query_vec"""
    def __init__(self, model):
        self.model = gensim.models.Word2Vec.load(model)
        # load wiki model in

    def get(self, keyword):
        result = self.model.most_similar(keyword, topn=1000)
        # query similar vocabulary with keyword
        return result

    def saveAsJson(self, result):
        f = codecs.open('w2v.tmp','w', encoding='utf-8')
        # codecs can write file with uft-8, which show chinese character correctly
        json.dump(result, f)

if __name__  ==  "__main__":
    if len(sys.argv) < 3:
        #sys.argv[0]是模組名稱喔!
        print("Usage:\n\tpython "+sys.argv[0]+" [name of model] "+"[query_keyword]")
        sys.exit(1)#0為正常絃拋出一個例外，可以被捕獲
    #print unicode(sys.argv[2], 'utf-8')
    q = query_vec(sys.argv[1])
    # init a query_vec instance with argv, note that if you query with chinese, need to turn chinese into unicode, and also import __future__ form unicode_literal
    q.saveAsJson(q.get(unicode(sys.argv[2], 'utf-8')))