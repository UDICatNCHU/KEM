# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from kem import *
from udic_nlp_API.settings_database import uri
import json

multilanguage_model = {
	'zh': {
		'origin':KEM('zh', uri=uri, ngram=True),
		'ontology':KEM('zh', uri=uri, ngram=True, ontology=True)
	}
}

@queryString_required(['lang', 'keyword'])
def kem(request):
	"""
	due to the base directory settings of django, the model_path needs to be different when
	testing with this section.
	"""
	keyword = request.GET['keyword']
	lang = request.GET['lang']
	ontology = 'ontology' if 'ontology' in request.GET and bool(json.loads(request.GET['ontology'].lower())) else 'origin'
	result = multilanguage_model[lang][ontology].most_similar(keyword, int(request.GET['num']) if 'num' in request.GET else 10)
	return JsonResponse(result, safe=False)

@queryString_required(['lang', 'keyword'])
def vector(request):
	keyword = request.GET['keyword']
	lang = request.GET['lang']
	ontology = 'ontology' if 'ontology' in request.GET else 'origin'
	result = multilanguage_model[lang][ontology].getVect(keyword)
	return JsonResponse(result, safe=False)

@queryString_required(['lang', 'k1', 'k2'])
def similarity(request):
	k1, k2 = request.GET['k1'], request.GET['k2']
	lang = request.GET['lang']
	ontology = 'ontology' if 'ontology' in request.GET else 'origin'
	result = multilanguage_model[lang][ontology].similarity(k1, k2)
	return JsonResponse(result, safe=False)