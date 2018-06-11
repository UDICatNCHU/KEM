# author: Shane Yu, CHANG, TAI-WEI  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
import subprocess, logging, json, os, math
from udic_nlp_API.settings_database import uri
from udicOpenData.stopwords import rmsw
import multiprocessing as mp
from kcem.apps import KCEM

logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s', filename='buildKEM.log', level=logging.INFO)
class BuildKem(object):
	"""
	build class can build the word2vec model automatically from downloading the wiki raw data all the way to the training porcess,
	and the model will be created in the CURRENT directory.

	constructors to be initialized:
	1) dimension of the model to be trained(integer)

	ps. An extra directiory will be created during the process.
	"""
	def __init__(self, lang, dimension, cpus, ontology=False):
		# object variable
		self.lang = lang
		self.wiki_dir_name = 'Wikipedia_{}'.format(lang)
		self.dimension = dimension
		self.ontology = ontology
		self.cpus = cpus

		# input files
		self.wiki_dump = os.path.join(self.wiki_dir_name, '{}wiki-latest-pages-articles.xml.bz2'.format(self.lang))

		# output files
		self.wiki_texts = os.path.join(self.wiki_dir_name, 'wiki_texts.{}.txt'.format(self.lang))
		self.wiki_seg = os.path.join(self.wiki_dir_name, 'wiki_seg_{}.txt'.format(self.lang))
		self.wiki_seg_kcem = os.path.join(self.wiki_dir_name, 'wiki_seg_kcem.{}.txt'.format(self.lang))

	def getWikiData(self):
		subprocess.call(['mkdir', self.wiki_dir_name])
		url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-pages-articles.xml.bz2'.format(self.lang, self.lang)
		if not os.path.exists(self.wiki_dump):
			subprocess.call(['wget', url,'-P', self.wiki_dir_name])

	def wikiToTxt(self):
		if os.path.exists(self.wiki_texts):
			return

		# This function takes about 25 minutes
		from gensim.corpora import WikiCorpus
		wiki_corpus = WikiCorpus(self.wiki_dump, dictionary={})
		
		texts_num = 0
		with open(self.wiki_texts, 'w', encoding='utf-8') as output:
			for text in wiki_corpus.get_texts():
				output.write(' '.join(text) + '\n')
				texts_num += 1
				if texts_num % 10000 == 0:
					logging.info("already processed %d articles" % texts_num)

	def segmentation(self):
		if os.path.exists(self.wiki_seg):
			return

		with open(self.wiki_seg, 'w', encoding='utf-8') as output:
			if self.lang == 'zh':
				# use opencc to translate chinese from simplified to tranditional
				subprocess.call(['opencc', '-i', self.wiki_texts, '-o', 'tmp'])
				subprocess.call(['mv', 'tmp', self.wiki_texts])
				with open(self.wiki_texts,'r', encoding='utf-8') as articles:
					# jieba segmentaion
					# takes about 30 minutes
					for texts_num, article in enumerate(articles):
						for word in rmsw(article):
							output.write(word +' ')
						output.write('\n')
						if texts_num % 10000 == 0:
							logging.info("Finish segmentation of line No.%d " % texts_num)
			elif self.lang == 'ja':
				import MeCab
				mecab = MeCab.Tagger("-Ochasen")
				with open(self.wiki_texts,'r', encoding='utf-8') as articles:
					for texts_num, article in enumerate(articles):
						for word in (i.split('\t')[0] for i in mecab.parse(article).split('\n')[:-2]):
							output.write(word +' ')
						output.write('\n')
						if texts_num % 10000 == 0:
							logging.info("Finish segmentation of line No.%d " % texts_num)


	def keyword2hypernym(self):
		if os.path.exists(self.wiki_seg_kcem):
			return

		# 判断一个unicode是否是汉字
		def is_chinese(keyword):
			for uchar in keyword:
				if '\u4e00' <= uchar<='\u9fff':
					continue
				else:
					return False
			return True

		def convert2KCEM(articles):
			process_id = os.getpid()
			kcem = KCEM('zh', uri, ngram=True)
			hypernym_mapping_table = {}
			with open(self.wiki_seg_kcem + '.{}'.format(process_id),'w', encoding='utf-8') as f:
				for article in articles:
					for index, word in enumerate(article):
						if word in hypernym_mapping_table:
							article[index] = hypernym_mapping_table[word]
						elif word in kcem.kcemNgram:
							hypernym = kcem.get(word)['value']
							if hypernym:
								hypernym_mapping_table[word] = hypernym[0][0]
								article[index] = hypernym[0][0]

					f.write(' '.join(article) + '\n')

		articles = [i.split() for i in open(self.wiki_seg, 'r', encoding='utf-8')]
		amount = math.ceil(len(articles)/self.cpus)
		articles = [articles[i:i + amount] for i in range(0, len(articles), amount)]
		processes = [mp.Process(target=convert2KCEM, kwargs={'articles':articles[i]}) for i in range(self.cpus)]

		logging.info('start thread')
		for process in processes:
			process.start()

		# Wait for all threads to complete
		for process in processes:
			process.join()

		# merge multiple wiki_seg_kcem files into one txt
		filenames = [os.path.join(self.wiki_dir_name, fname) for fname in os.listdir(self.wiki_dir_name) if fname.startswith('wiki_seg_kcem')]
		with open(self.wiki_seg_kcem, 'w', encoding='utf-8') as mergefile:
			# merge wiki_seg_kcem files generated by multiprocess
			for fname in filenames:
				with open(fname, 'r', encoding='utf-8') as infile:
					mergefile.write(infile.read())
				os.remove(fname)

			# also, concatenate original wiki_seg file to make sure it contains vectors of both hypernyms and hyponyms.
			with open(self.wiki_seg, 'r', encoding='utf-8') as infile:
				mergefile.write(infile.read())

	def train(self):
		from gensim.models import word2vec

		if self.ontology:
			# Experimental function, use ontology to build new word2vec.
			sentences = word2vec.Text8Corpus(self.wiki_seg_kcem)
		else:
			# normal process of building word2vec model
			sentences = word2vec.Text8Corpus(self.wiki_seg)

		model = word2vec.Word2Vec(sentences, size=self.dimension, workers=mp.cpu_count())

		# Save our model.
		model.wv.save_word2vec_format('./med{}.model.bin.{}.{}'.format(str(self.dimension), self.lang, str(self.ontology)), binary=True)


	def main(self):
		print('========================== Download Wiki Dump ==========================')			
		self.getWikiData()
		print('========================== Extract Wiki Dump ==========================')
		self.wikiToTxt()
		print('========================== Do Segmentation ==========================')
		self.segmentation()
		print('========================== Start Training ==========================')
		if self.ontology:
			print('========================== [Experimental Feature] Use kcem to replace keywords into hypernym before training ==========================')
			self.keyword2hypernym()
		self.train()
		print('========================== Finish Training: ' + str(self.dimension) + ' Dimensions ==========================')

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
		parser.add_argument('--cpus', type=int, default=6)

	def handle(self, *args, **options):
		obj = BuildKem(options['lang'], options['dimension'], options['cpus'], options['ontology'])
		obj.main()
		self.stdout.write(self.style.SUCCESS('build kem model success!!!'))