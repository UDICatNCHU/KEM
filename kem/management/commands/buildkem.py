# author: Shane Yu, CHANG, TAI-WEI  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
import subprocess, logging, json, multiprocessing, jieba
from udic_nlp_API.settings_database import uri
from udicOpenData.dictionary import *
from udicOpenData.stopwords import *

logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', filename='buildKEM.log', level=logging.INFO)
class build(object):
	"""
	build class can build the word2vec model automatically from downloading the wiki raw data all the way to the training porcess,
	and the model will be created in the CURRENT directory.

	constructors to be initialized:
	1) dimension of the model to be trained(integer)

	ps. An extra directiory will be created during the process.
	"""
	def __init__(self, lang, wiki_dir_name, dimension, ontology=False):
		self.lang = lang
		self.wiki_dir_name = wiki_dir_name
		self.dimension = dimension
		self.ontology = ontology
		self.keyword2entityList = []

	def wikiToTxt(self):
		# This function takes about 25 minutes
		from gensim.corpora import WikiCorpus

		wiki_corpus = WikiCorpus(os.path.join(self.wiki_dir_name, '{}wiki-latest-pages-articles.xml.bz2'.format(self.lang)), dictionary={})
		
		texts_num = 0
		with open(os.path.join(self.wiki_dir_name, 'wiki_texts.txt'), 'w', encoding='utf-8') as output:
			for text in wiki_corpus.get_texts():
				output.write(' '.join(text) + '\n')
				texts_num += 1
				if texts_num % 10000 == 0:
					logging.info("已處理 %d 篇文章" % texts_num)


	def opencc(self):
		subprocess.call(['opencc', '-i', os.path.join(self.wiki_dir_name, 'wiki_texts.txt'), '-o', os.path.join(self.wiki_dir_name, 'wiki_{}.txt'.format(self.lang))])

	def segmentation(self):
		# takes about 30 minutes

		output = open(os.path.join(self.wiki_dir_name, 'wiki_seg_{}.txt'.format(self.lang)), 'w')
		
		texts_num = 0
		
		with open(os.path.join(self.wiki_dir_name, 'wiki_{}.txt'.format(self.lang)),'r') as articles:
			for article in articles:
				for word in rmsw(article):
					output.write(word +' ')
				output.write('\n')
				texts_num += 1
				if texts_num % 10000 == 0:
					logging.info("已完成前 %d 行的斷詞" % texts_num)
		output.close()

	def keyword2entity(self):
		from collections import defaultdict
		import pyprind, math, pymongo, threading
		from udic_nlp_API.settings import W2VMODEL
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
		ConvertKeywordSet = {i for i in W2VMODEL.vocab.keys() if is_chinese(i)}
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


		with open(os.path.join(self.wiki_dir_name, 'wiki_seg_{}.txt'.format(self.lang)), 'r') as f:
			text = f.read().split()
			try:
				invertedIndex = json.load(open(os.path.join(self.wiki_dir_name, 'invertedIndex.json'), 'r'))
			except Exception as e:
				invertedIndex = defaultdict(list)
				for index, word in pyprind.prog_bar(list(enumerate(text))):
					invertedIndex[word].append(index)
				json.dump(invertedIndex, open(os.path.join(self.wiki_dir_name, 'invertedIndex.json'), 'w'))

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
		with open(os.path.join(self,wiki_dir_name, 'wiki_seg_replace.txt'),'w', encoding='utf-8') as f:
			f.write(wiki_string)

	def train(self):
		from gensim.models import word2vec

		if self.ontology:
			# 使用ontology的實驗性功能，去建立word2vec
			sentences = word2vec.Text8Corpus(os.path.join(self.wiki_dir_name, 'wiki_seg_replace.txt'))
		else:
			# 正常版的word2vec
			sentences = word2vec.Text8Corpus(os.path.join(self.wiki_dir_name, 'wiki_seg_{}.txt'.format(self.lang)))

		model = word2vec.Word2Vec(sentences, size=self.dimension, workers=multiprocessing.cpu_count())

		# Save our model.
		model.wv.save_word2vec_format('./med{}.model.bin.{}'.format(str(self.dimension), self.lang), binary=True)


	def exec(self):
		print('========================== 開始下載wiki壓縮檔 ==========================')
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
		parser.add_argument('--dimension', type=int, default=400)
		parser.add_argument(
			'--ontology',
			default=False,
			type=bool,
			help='use Ontology result to rebuild word2vec to extract relations and axioms',
		)
		parser.add_argument('--lang', type=str)

	def handle(self, *args, **options):
		def getWikiData():
			wiki_dir_name = 'Wikipedia'
			wiki_json_dir = 'wikijson'

			subprocess.call(['mkdir', wiki_dir_name])
			subprocess.call(['mkdir', wiki_json_dir])
			lang = options['lang']
			url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-pages-articles.xml.bz2'.format(lang, lang)
			if not os.path.exists(os.path.join(wiki_dir_name, '{}wiki-latest-pages-articles.xml.bz2'.format(lang))):
				subprocess.call(['wget', url,'-P', wiki_dir_name])
				subprocess.call(['WikiExtractor.py', os.path.join(wiki_dir_name, '{}wiki-latest-pages-articles.xml.bz2'.format(lang)), '-o', wiki_json_dir, '--json'])
			return wiki_dir_name, wiki_json_dir, lang

		wiki_dir_name, wiki_json_dir, lang = getWikiData()
		# 1) dimension of the model to be trained
		# obj = build(400) # examples 
		obj = build(lang, wiki_dir_name, options['dimension'], options['ontology'])
		obj.exec()

		self.stdout.write(self.style.SUCCESS('build kem model success!!!'))