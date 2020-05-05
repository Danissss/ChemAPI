import json

from django.shortcuts import render
from django.http import HttpResponse

from rapidminer.core import retentionIndexPredict

# Create your views here.


def predict(request, structure):
	response_data = {}
	retention_index = retentionIndexPredict.single_run(structure)
	response_data['rapidminer'] = str(retention_index)
	return HttpResponse(json.dumps(response_data), content_type="application/json") 

