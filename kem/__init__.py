# author: Shane Yu  date: April 8, 2017
# author: Chang Tai-Wei  date: April 8, 2017

class KEM(object):
    """
    KEM class uses MongoDB as a cache to accelerate the process of querying kem model,
    most_similar() function returns a list of query result from MongoDB if the query term exists in
    the database(fast), and only do the gensim built-in query function when the query term is not
    in the database(slow).
    """
    def __init__(self, uri):
        from ngram import NGram
        from udic_nlp_API.settings import W2VMODEL
        self.model = W2VMODEL

        # ngram search
        self.kemNgram = NGram(self.model.wv.vocab.keys())

    def most_similar(self, keyword, num):
        """
        input: keyword term of top n
        output: keyword result in json formmat
        """
        try:
            result = self.model.most_similar(keyword, topn = num) # most_similar return a list
            return {'key':keyword, 'value':result, 'similarity':1}
        except KeyError as e:
            kemKeyword = self.kemNgram.find(keyword)
            if kemKeyword:
                result = self.model.most_similar(kemKeyword, topn = num)
                return {'key':kemKeyword, 'value':result, 'similarity':self.kemNgram.compare(kemKeyword, keyword)}
            return {'key':keyword, 'value':[], 'similarity':0}

    def getVect(self, keyword):
        try:
            result = self.model[keyword].tolist()
        except KeyError as e:
            keyword = self.kemNgram.find(keyword)
            if keyword == None:
                return [0]*400
            result = self.model[keyword].tolist()
        return {'key':keyword, 'value':result}

if __name__ == '__main__':
    import sys
    obj = KEM('mongodb://140.120.13.244:7777/')
    temp = obj.most_similar(sys.argv[1], 100)
    print(temp)