# author: Shane Yu  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
import subprocess, logging, json
from kcem.utils.utils import criteria
from kcem.utils.utils import model as w2vModel
from kcem.views import kcem_new as kcemNewRequest
from django.http import HttpRequest



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


    def creatBuildDir(self):
        subprocess.call(['mkdir', 'build'])


    def getWiki(self):
        subprocess.call(['wget', 'https://dumps.wikimedia.org/zhwiki/latest/zhwiki-latest-pages-articles.xml.bz2', '-P', './build/'])


    def wikiToTxt(self):
        # This function takes about 25 minutes
        from gensim.corpora import WikiCorpus

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
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

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

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
        import pandas as pd
        import pyprind
        # 判断一个unicode是否是汉字
        def is_chinese(uchar):         
            if '\u4e00' <= uchar<='\u9fff':
                return True
            else:
                return False

        keywordList = sorted([i for i in w2vModel.vocab.keys() if len(i) >2 and is_chinese(i)], key=lambda x:len(x), reverse=True)

        with open('./build/wiki_seg.txt', 'r') as f:
            text = f.read().split()
        df = pd.DataFrame({'wiki': text})
        httpReq = HttpRequest()
        httpReq.method = 'GET'

        for keyword in pyprind.prog_bar(keywordList):
            httpReq.GET['keyword'] = keyword
            entity = json.loads(kcemNewRequest(httpReq).getvalue().decode('utf-8'))
            print(keyword)
            if len(entity):
                df = df.replace(to_replace=[keyword], value=[entity[0][0]] )

        wiki_json = json.loads(df.to_json())
        json.dump(wiki_json, open('wiki.replace.json','w'))
        wiki_string = ' '.join([wiki_json[str(index[0])] for index in enumerate(wiki_json)])
        with open('./build/wiki_seg_replace.txt','w', encoding='utf-8') as f:
            f.write(wiki_string)

    def train(self):
        from gensim.models import word2vec
        import multiprocessing

        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

        if self.ontology:
            # 使用ontology的實驗性功能，去建立word2vec
            sentences = word2vec.Text8Corpus('./build/wiki_seg_replace.txt')
        else:
            # 正常版的word2vec
            sentences = word2vec.Text8Corpus('./build/wiki_seg.txt')

        model = word2vec.Word2Vec(sentences, size=self.dimension, workers=multiprocessing.cpu_count())

        # Save our model.
        model.wv.save_word2vec_format('./med' + str(self.dimension) + '.model.bin', binary=True)


    def exec(self):
        print('========================== 開始下載wiki壓縮檔 ==========================')
        self.getWiki()
        print('========================== wiki壓縮檔下載完畢，開始將壓縮檔轉成文字檔 ==========================')
        self.wikiToTxt()
        print('========================== 壓縮檔轉文字檔過程完畢，開始繁轉簡過程 ==========================')
        self.opencc()
        print('========================== 繁轉簡過程完畢，開始斷詞 ==========================')
        self.segmentation()
        print('========================== 斷詞完畢，開始訓練model ==========================')
        if self.ontology:
            self.keyword2entity()
            print('========================== 用kcem把單子轉成entity ==========================')
        self.train()
        print('========================== ' + str(self.dimension) + '維model訓練完畢，model存放在當前目錄 ==========================')

class Command(BaseCommand):
    help = 'use this for build model of KEM!'
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--jiebaDict', type=str)
        parser.add_argument('--stopword', type=str)
        parser.add_argument('--dimension', type=int)
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