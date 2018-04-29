# author: Shane Yu  date: April 8, 2017
# author: Chang Tai-Wei  date: April 8, 2017
import gensim
from ngram import NGram

class KEM(object):
    """
    KEM class uses MongoDB as a cache to accelerate the process of querying kem model,
    most_similar() function returns a list of query result from MongoDB if the query term exists in
    the database(fast), and only do the gensim built-in query function when the query term is not
    in the database(slow).
    """
    def __init__(self, lang, uri):
        self.model = gensim.models.KeyedVectors.load_word2vec_format('med400.model.bin.{}'.format(lang), binary=True)

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
            return {'key':keyword, 'value':result, 'similarity':1}
        except KeyError as e:
            kemKeyword = self.kemNgram.find(keyword)
            if kemKeyword:
                result = self.model[kemKeyword].tolist()
                return {'key':kemKeyword, 'value':result, 'similarity':self.kemNgram.compare(kemKeyword, keyword)}
            return {'key':keyword, 'value':[0]*400, 'similarity':0}

    def similarity(self, k1, k2):
        try:
            similarity = self.model.similarity(k1, k2)
            return {'k1': k1, 'k2':k2, 'similarity':similarity, 'k1Similarity':1, 'k2Similarity':1}
        except KeyError as e:
            try:
                if k1 not in self.kemNgram and k2 not in self.kemNgram:
                    k1Ngram = self.kemNgram.find(k1)
                    k2Ngram = self.kemNgram.find(k2)
                    similarity = self.model.similarity(k1Ngram, k2Ngram)
                    return {'k1': k1Ngram, 'k2':k2Ngram, 'similarity':similarity, 'k1Similarity':self.kemNgram.compare(k1, k1Ngram), 'k2Similarity': self.kemNgram.compare(k2, k2Ngram)}                
                elif k1 not in self.kemNgram:
                    k1Ngram = self.kemNgram.find(k1)
                    similarity = self.model.similarity(k1Ngram, k2)
                    return {'k1': k1Ngram, 'k2':k2, 'similarity':similarity, 'k1Similarity':self.kemNgram.compare(k1, k1Ngram), 'k2Similarity': 1}
                else:
                    k2Ngram = self.kemNgram.find(k2)
                    similarity = self.model.similarity(k1, k2Ngram)
                    return {'k1': k1, 'k2':k2Ngram, 'similarity':similarity, 'k1Similarity':1, 'k2Similarity': self.kemNgram.compare(k2, k2Ngram)}
            except KeyError as e:
                return {}

if __name__ == '__main__':
    import sys
    obj = KEM('mongodb://140.120.13.244:7777/')
    temp = obj.most_similar(sys.argv[1], 100)
    print(temp)