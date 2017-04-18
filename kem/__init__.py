# author: Shane Yu  date: April 8, 2017
import json

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
        self.db = self.client['kem']
        self.coll = self.db['kem_coll']
        self.model_path = model_path
        

    def getTerms(self, query, num):
        """
        input: query term, number of top n
        output: query result in json formmat
        """
        result = self.coll.find({'Term':query}, {'Result':1, '_id':False}).limit(1) # print(type(result)) # <class 'pymongo.cursor.Cursor'>
        if result.count() == 0:
            resultJson = self.getJsonResult(query, num)
            self.insertMongo(query, resultJson)
            return resultJson

        return (list(result)[0])['Result']


    def insertMongo(self, queryTerm, resultList):
        state = self.coll.insert({'Term':queryTerm, 'Result':resultList})
        print(state)


    def getJsonResult(self, queryStr, number):
        """
        input: query term
        output: query result from gensim built-in query function in json formmat
        """
        from gensim import models
        from gensim.models import word2vec
        try:
            print('Running most_similar function')
            model = models.KeyedVectors.load_word2vec_format(self.model_path, binary=True)
            res = model.most_similar(queryStr, topn = number) # most_similar return a list
            print(queryStr + '相似詞前' + str(number) + '排序')
            resJson = json.dumps(res)

            return resJson

        except Exception as e:
            print(repr(e))



if __name__ == '__main__':
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
