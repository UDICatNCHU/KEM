# author: Shane Yu  date: April 8, 2017
# author: Chang Tai-Wei  date: April 8, 2017
import pickle
import gensim
from ngram import NGram

class KEM(object):
    def __init__(self, lang, uri, ngram=False, ontology=False):
        self.model = gensim.models.KeyedVectors.load_word2vec_format('med400.model.bin.{}.{}'.format(lang, str(ontology)), binary=True).wv

        if ngram:
            try:
                self.kemNgram = pickle.load(open('kemNgram.{}.pkl'.format(self.lang), 'rb'))
            except FileNotFoundError as e:
                print(str(e)+', if this happened in building steps, then ignore it!')

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