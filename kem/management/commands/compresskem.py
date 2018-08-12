# author: Shane Yu, CHANG, TAI-WEI  date: April 8, 2017
from django.core.management.base import BaseCommand, CommandError
import gensim, json
import numpy as np
from udic_nlp_API.settings_database import uri
from kcem.apps import KCEM
from tqdm import tqdm
from collections import defaultdict
from pathlib import Path
from gensim.models.keyedvectors import Word2VecKeyedVectors

class Command(BaseCommand):
	help = 'use this command to build compress word2vec'

	def add_arguments(self, parser):
		# Positional arguments
		parser.add_argument('--lang', type=str)

	def handle(self, *args, **options):
		ORIGINAL_MODEL = gensim.models.KeyedVectors.load_word2vec_format('med400.model.bin.{}.False'.format(options['lang']), binary=True).wv
		ONTOLOTY_MODEL = gensim.models.KeyedVectors.load_word2vec_format('med400.model.bin.{}.True'.format(options['lang']), binary=True).wv
		kcem = KCEM(lang='zh', uri=uri, cpus=int(1), ngram=True)
		KCEM_INVERTED_INDEX = defaultdict(list)

		# turn word2vec into hypernyms
		# and record these relation in a inverted index
		if not Path('word2vec.compress.json').exists():
			for index, keyword in tqdm(enumerate(ORIGINAL_MODEL.wv.vocab)):
				# if index == 10000:
				# 	break
				response = kcem.get(keyword)['value']
				if len(response):
					hypernym = response[0][0]
					KCEM_INVERTED_INDEX[hypernym].append(keyword)

			json.dump(KCEM_INVERTED_INDEX, open('word2vec.compress.json', 'w'))
		else:
			KCEM_INVERTED_INDEX = json.load(open('word2vec.compress.json', 'r'))
		# initialize compress word2vec
		# COMPRESS_MODEL = Word2VecKeyedVectors(3065)

		vocab = {}
		index = 0
		for keyword in KCEM_INVERTED_INDEX:
			try:
				Vocab_object = ONTOLOTY_MODEL.vocab[keyword]
				Vocab_object.index = index
				index += 1
				vocab[keyword] = Vocab_object
			except Exception as e:
				print(keyword)
				continue
		print(len(KCEM_INVERTED_INDEX))
		print(len(vocab))
		COMPRESS_MODEL = Word2VecKeyedVectors(len(vocab))
		COMPRESS_MODEL.vocab = vocab
		print(len(COMPRESS_MODEL.vocab))
		# initialize vertor array
		COMPRESS_MODEL.vectors = np.zeros((len(COMPRESS_MODEL.vocab), 400))
		for keyword, Vocab_object in COMPRESS_MODEL.vocab.items():
			index = Vocab_object.index
			COMPRESS_MODEL.vectors[index] = ONTOLOTY_MODEL[keyword]
		COMPRESS_MODEL.save_word2vec_format('./med400.model.bin.{}.True.gz'.format(options['lang']), binary=True)

		self.stdout.write(self.style.SUCCESS('build word2vec.compress.json success!!!'))