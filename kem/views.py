# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from kem import *
from udic_nlp_API.settings_database import uri

multilanguage_model = {
	'zh': KEM('zh', uri=uri)
}

@queryString_required(['lang', 'keyword'])
def kem(request):
	"""
	due to the base directory settings of django, the model_path needs to be different when
	testing with this section.
	"""
	keyword = request.GET['keyword']
	lang = request.GET['lang']
	result = multilanguage_model[lang].most_similar(keyword, int(request.GET['num']) if 'num' in request.GET else 10)
	return JsonResponse(result, safe=False)

@queryString_required(['lang', 'keyword'])
def vector(request):
	keyword = request.GET['keyword']
	lang = request.GET['lang']
	result = multilanguage_model[lang].getVect(keyword)
	return JsonResponse(result, safe=False)

@queryString_required(['lang', 'k1', 'k2'])
def similarity(request):
	k1, k2 = request.GET['k1'], request.GET['k2']
	lang = request.GET['lang']
	result = multilanguage_model[lang].similarity(k1, k2)
	return JsonResponse(result, safe=False)