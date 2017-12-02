from ngram import NGram

# author: Shane Yu  date: April 8, 2017
# author: Chang Tai-Wei  date: April 8, 2017

class KEM(object):
    """
    KEM class uses MongoDB as a cache to accelerate the process of querying kem model,
    most_similar() function returns a list of query result from MongoDB if the query term exists in
    the database(fast), and only do the gensim built-in query function when the query term is not
    in the database(slow).
    """
    def __init__(self, uri, model_path = './KEM/med400.model.bin'):
        from gensim import models
        self.model = models.KeyedVectors.load_word2vec_format(model_path, binary=True)

        # ngram search
        self.modelNgram = NGram(self.model.wv.vocab.keys())

    def most_similar(self, keyword, num):
        """
        input: keyword term of top n
        output: keyword result in json formmat
        """
        try:
            return self.model.most_similar(keyword, topn = num) # most_similar return a list
        except KeyError as e:
            return self.model.most_similar(self.modelNgram.find(keyword), topn = num)

    def getVect(self, keyword):
        try:
            return self.model[keyword].tolist()
        except KeyError as e:
            return self.model[self.modelNgram.find(keyword)].tolist()        

if __name__ == '__main__':
    import json
    """
    due to the base directory settings of django, the model_path needs to be different when
    testing with this section.
    """
    import sys
    obj = KEM('mongodb://140.120.13.244:7777/', model_path = './med400.model.bin')
    temp = obj.most_similar(sys.argv[1], 100)
    print(temp)