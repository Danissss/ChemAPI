
import json

from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from . import helper

def predictAll(request, structure):
	conventionalName, descriptorName = helper.getDescriptorName()
	mol = helper.getMolFromSmiles(structure)
	descriptorv = helper.getMolecularDescriptor(mol, descriptorName)
	response_data = {}

	for i in range(0,len(descriptorv)):
		response_data[conventionalName[i]] = descriptorv[i]

	logS = helper.predictLogS(mol)
	response_data["LogS"] = logS
	logD = helper.predictLogD(mol)
	response_data["LogD"] = logD

	return HttpResponse(json.dumps(response_data), content_type="application/json")


def predictLogS(request, structure):
	response_data = {}
	mol = helper.getMolFromSmiles(structure)
	logS = helper.predictLogS(mol)
	response_data["LogS"] = logS
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def predictLogD(request, structure):
	response_data = {}
	mol = helper.getMolFromSmiles(structure)
	logD = helper.predictLogD(mol)
	response_data["LogD"] = logD
	return HttpResponse(json.dumps(response_data), content_type="application/json")

