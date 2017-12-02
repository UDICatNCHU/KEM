# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from kem import KEM
from udic_nlp_API.settings_database import uri
obj = KEM(uri=uri, model_path = './med400.model.bin')

@queryString_required(['keyword'])
def kem(request):
    """
    due to the base directory settings of django, the model_path needs to be different when
    testing with this section.
    """
    keyword = request.GET['keyword']
    result = obj.most_similar(keyword, int(request.GET['num']) if 'num' in request.GET else 10)
    return JsonResponse(result, safe=False)

@queryString_required(['keyword'])
def vector(request):
	keyword = request.GET['keyword']
	result = obj.getVect(keyword)
	return JsonResponse(result, safe=False)

