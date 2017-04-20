# author: Shane Yu  date: April 8, 2017

class KEM(object):
    """
    KEM class uses MongoDB as a cache to accelerate the process of querying kem model,
    getTerms() function returns a list of query result from MongoDB if the query term exists in
    the database(fast), and only do the gensim built-in query function when the query term is not
    in the database(slow).
    """
    def __init__(self, uri, model_path = './KEM/med400.model.bin'):
        from pymongo import MongoClient
        self.client = MongoClient(uri)
        self.db = self.client['nlp']
        self.coll = self.db['kem']
        self.model_path = model_path
        

    def getTerms(self, query, num):
        """
        input: query term of top n
        output: query result in json formmat
        """
        result = self.coll.find({'Term':query}, {'Result':1, '_id':False}).limit(1) # print(type(result)) # <class 'pymongo.cursor.Cursor'>
        if result.count() == 0:
            resultJson = self.getJsonResult(query)
            self.insertMongo(query, resultJson)
            return resultJson[:num]

        return (list(result)[0])['Result'][:num]


    def insertMongo(self, queryTerm, resultList):
        state = self.coll.insert({'Term':queryTerm, 'Result':resultList})

    def getJsonResult(self, queryStr):
        """
        input: query term
        output: query result from gensim built-in query function in json formmat
        """
        from gensim import models
        try:
            model = models.Word2Vec.load_word2vec_format(self.model_path, binary=True)
            res = model.most_similar(queryStr, topn = 1000) # most_similar return a list
            return res

        except Exception as e:
            print(repr(e))
            raise e

if __name__ == '__main__':
    import json
    """
    due to the base directory settings of django, the model_path needs to be different when
    testing with this section.
    """
    import sys
    obj = KEM('mongodb://140.120.13.244:7777/', model_path = './med400.model.bin')
    temp = obj.getTerms(sys.argv[1], 100)
    if temp:
        for item in json.loads(temp):
            print(item)
    else:
        print(sys.argv[1] + 'Not in the dictionary.')
