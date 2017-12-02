# author: Shane Yu  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
import subprocess, logging, json, multiprocessing
from kcem.utils.utils import model as w2vModel
from udic_nlp_API.settings_database import uri


logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', filename='buildKEM.log', level=logging.INFO)
class build(object):
    """
    build class can build the word2vec model automatically from downloading the wiki raw data all the way to the training porcess,
    and the model will be created in the CURRENT directory.

    constructors to be initialized:
    1) path of customized jieba dictionarty
    2) path of stopwords
    3) dimension of the model to be trained(integer)

    ps. An extra directiory will be created during the process.
    """
    def __init__(self, ontology, jiebaDictPath, stopwordsPath, dimension):
        self.ontology = ontology
        self.jiebaDictPath = jiebaDictPath
        self.stopwordsPath = stopwordsPath
        self.dimension = dimension
        self.keyword2entityList = []

    def creatBuildDir(self):
        subprocess.call(['mkdir', 'build'])


    def getWiki(self):
        subprocess.call(['wget', 'https://dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2', '-P', './build/'])


    def wikiToTxt(self):
        # This function takes about 25 minutes
        from gensim.corpora import WikiCorpus

        wiki_corpus = WikiCorpus('./build/zhwiki-latest-pages-articles.xml.bz2', dictionary={})
        
        texts_num = 0
        with open('./build/wiki_texts.txt', 'w', encoding='utf-8') as output:
            for text in wiki_corpus.get_texts():
                output.write(b' '.join(text).decode('utf-8') + '\n')
                texts_num += 1
                if texts_num % 10000 == 0:
                    logging.info("已處理 %d 篇文章" % texts_num)


    def opencc(self):
        subprocess.call(['opencc', '-i', './build/wiki_texts.txt', '-o', './build/wiki_zh_tw.txt'])

    def segmentation(self):
        # takes about 30 minutes
        import jieba

        # jieba custom setting.
        jieba.set_dictionary(self.jiebaDictPath)

        # load stopwords set
        stopwordset = set()
        for i in json.load(open(self.stopwordsPath, 'r', encoding='utf-8')):
            stopwordset.add(i)                

        output = open('./build/wiki_seg.txt', 'w')
        
        texts_num = 0
        
        with open('./build/wiki_zh_tw.txt','r') as content :
            for line in content:
                words = jieba.cut(line, cut_all=False)
                for word in words:
                    if word not in stopwordset:
                        output.write(word +' ')
                texts_num += 1
                if texts_num % 10000 == 0:
                    logging.info("已完成前 %d 行的斷詞" % texts_num)
        output.close()

    def keyword2entity(self):
        from collections import defaultdict
        import pyprind, math, pymongo, threading
        self.Collect = pymongo.MongoClient(uri)['nlp']['kcem']
        # 判断一个unicode是否是汉字
        def is_chinese(keyword):
            for uchar in keyword:
                if '\u4e00' <= uchar<='\u9fff':
                    continue
                else:
                    return False
            return True

        # 需要實驗才知道，哪些單字需要透過kcem做轉換
        ConvertKeywordSet = {i for i in w2vModel.vocab.keys() if is_chinese(i)}
        threadLock = threading.Lock()

        def convert2KCEM(InvertedIndexList):
            for index, pair in enumerate(InvertedIndexList):
                key = pair[0]
                value = pair[-1]
                if key not in ConvertKeywordSet:
                    continue

                entity = self.Collect.find({'key':key}, {'value':1, '_id':False}).limit(1)
                if entity.count() == 0:
                    continue
                try:
                    entity = dict(list(entity)[0])['value']
                    if len(entity):
                        InvertedIndexList[index] = (entity[0][0], value)
                except Exception as e:
                    entity = self.Collect.find({'key':key}, {'value':1, '_id':False}).limit(1)
                    print(list(entity), pair, index)
                if index % 100 == 0:
                    logging.info("已處理 %d 個單子" % index)
            threadLock.acquire()
            self.keyword2entityList += InvertedIndexList
            threadLock.release()


        with open('./build/wiki_seg.txt', 'r') as f:
            text = f.read().split()
            try:
                invertedIndex = json.load(open('./build/invertedIndex.json', 'r'))
            except Exception as e:
                invertedIndex = defaultdict(list)
                for index, word in pyprind.prog_bar(list(enumerate(text))):
                    invertedIndex[word].append(index)
                json.dump(invertedIndex, open('./build/invertedIndex.json', 'w'))

            invertedIndexItem = list(invertedIndex.items())
            step = math.ceil(len(invertedIndexItem)/multiprocessing.cpu_count())
            invertedIndexItem = [invertedIndexItem[i:i + step] for i in range(0, len(invertedIndexItem), step)]

        workers = [threading.Thread(target=convert2KCEM, kwargs={'InvertedIndexList':invertedIndexItem[i]}, name=str(i)) for i in range(multiprocessing.cpu_count())]

        logging.info('start thread')
        for thread in workers:
           thread.start()

        # Wait for all threads to complete
        for thread in workers:
            thread.join()

        # convert self.keyword2entityList from inverted Index format into plain text format, just like `text = f.read().split()`
        # and then i'll use ' '.join to turn it back into original text format.
        textList = [None] * (len(text))
        for keyword, indexList in self.keyword2entityList:
            for index in indexList:
                textList[index] = keyword
        wiki_string = ' '.join(textList)
        with open('./build/wiki_seg_replace.txt','w', encoding='utf-8') as f:
            f.write(wiki_string)

    def train(self):
        from gensim.models import word2vec

        if self.ontology:
            # 使用ontology的實驗性功能，去建立word2vec
            sentences = word2vec.Text8Corpus('./build/wiki_seg_replace.txt')
        else:
            # 正常版的word2vec
            sentences = word2vec.Text8Corpus('./build/wiki_seg.txt')

        model = word2vec.Word2Vec(sentences, size=self.dimension, workers=multiprocessing.cpu_count())

        # Save our model.
        model.wv.save_word2vec_format('./build/med' + str(self.dimension) + '.model.bin', binary=True)


    def exec(self):
        # print('========================== 開始下載wiki壓縮檔 ==========================')
        # self.getWiki()
        # print('========================== wiki壓縮檔下載完畢，開始將壓縮檔轉成文字檔 ==========================')
        # self.wikiToTxt()
        # print('========================== 壓縮檔轉文字檔過程完畢，開始繁轉簡過程 ==========================')
        # self.opencc()
        # print('========================== 繁轉簡過程完畢，開始斷詞 ==========================')
        # self.segmentation()
        # print('========================== 斷詞完畢，開始訓練model ==========================')
        if self.ontology:
            self.keyword2entity()
            print('========================== 用kcem把單子轉成entity ==========================')
        self.train()
        print('========================== ' + str(self.dimension) + '維model訓練完畢，model存放在當前目錄 ==========================')

class Command(BaseCommand):
    help = 'use this for build model of KEM!'
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--jiebaDict', type=str, required=True)
        parser.add_argument('--stopword', type=str, required=True)
        parser.add_argument('--dimension', type=int, required=True)
        parser.add_argument(
            '--ontology',
            default=False,
            type=bool,
            help='use Ontology result to rebuild word2vec to extract relations and axioms',
        )

    def handle(self, *args, **options):
        # 1) jieba customized dictionary 2) stopwords text file 3) dimension of the model to be trained
        # obj = build('jieba_dict/dict.txt.big.txt', 'jieba_dict/stopwords.txt', 400) # examples 
        obj = build(options['ontology'], options['jiebaDict'], options['stopword'], options['dimension'])
        obj.exec()

        self.stdout.write(self.style.SUCCESS('build kem model success!!!'))