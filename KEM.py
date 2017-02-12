#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, subprocess, json
from os import path
from functools import wraps
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

class KEM(object):
    """ A KEM object having api for web to query
    Args:
        filePath: path to ptt json file.

    Returns:
        ptt articles with specific keyword.
    """
    def __init__(self, num, lang, ParentDir = '', uri=None):
        from pymongo import MongoClient
        self.WikiModelDirPath = 'word2vec'
        self.ParentDir = ParentDir
        self.lang = lang
        self.client = MongoClient(uri)
        self.db = self.client['nlp']
        self.Collect = self.db['kem']       

    def getTerms(self, keyword, num):
        def setDirPath(func):
            @wraps(func)
            def wrap(self, *args, **kw):
                self.DirPath = self.ParentDir + self.WikiModelDirPath
                return func(self, *args, **kw)
            return wrap

        @setDirPath
        def getFilePath(keyword):
            return '{}/{}/{}.{}'.format(self.DirPath, keyword, keyword, 'model')

        result = self.Collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1)
        if result.count() == 0:
            subprocess.call(['python2', 'KEM/querySoup.py', getFilePath(self.lang), keyword])
            with open('w2v.tmp', 'r') as f:
                result = json.load(f)
                value = sorted(result, key=lambda x:-x[1])
                self.Collect.insert({'key':keyword, 'value':value})
                return value[:num]

        return dict(list(result)[0])['value'][:num]