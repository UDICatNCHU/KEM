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
        self.model_path = model_path
        self.model = None
        self.client = MongoClient(uri)
        self.db = self.client['nlp']
        self.synonym = self.db['kem'] # 放同義字的collection
        self.vector = self.db['kemVec']  # 放向量的

    def getTerms(self, keyword, num):
        """
        input: keyword term of top n
        output: keyword result in json formmat
        """
        result = self.synonym.find({'Term':keyword}, {'Result':1, '_id':False}).limit(1)
        # return <class 'pymongo.cursor.Cursor'>
        if result.count() == 0:
            try:
                self.get_or_load_model()
                result = self.model.most_similar(keyword, topn = 1000) # most_similar return a list
                self.insertMongo(self.synonym, keyword, result)
                return result[:num]
            except KeyError as e:
                return []
            except Exception as e:
                raise e
        return (list(result)[0])['Result'][:num]

    def getVect(self, keyword):
        result = self.vector.find({'Term':keyword}, {'Result':1, '_id':False}).limit(1)
        if result.count() == 0:
            try:
                self.get_or_load_model()
                result = self.model[keyword].tolist()
                self.insertMongo(self.vector, keyword, result)
                return result
            except KeyError as e:
                return []
            except Exception as e:
                raise e
        return (list(result)[0])['Result']

    @staticmethod
    def insertMongo(collection, keyword, result):
        state = collection.insert({'Term':keyword, 'Result':result})

    def get_or_load_model(self):
        if self.model != None:
            return
        from gensim import models
        self.model = models.KeyedVectors.load_word2vec_format(self.model_path, binary=True)

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
