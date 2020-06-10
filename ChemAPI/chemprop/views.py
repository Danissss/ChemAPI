
import json

from django.shortcuts import render
from django.http import HttpResponse

from property_store.models import Property
from rdkit import Chem
from datetime import datetime
# Create your views here.

from . import helper

def predictAll(request, structure):
	conventionalName, descriptorName = helper.getDescriptorName()
	mol = helper.getMolFromSmiles(structure)
	descriptorv = helper.getMolecularDescriptor(mol, descriptorName)
	response_data = {}

	for i in range(0,len(descriptorv)):
		response_data[conventionalName[i]] = descriptorv[i]

	# logS = helper.predictLogS(mol)
	response_data["LogS"] = single_run_log_s(structure)
	# logD = helper.predictLogD(mol)
	response_data["LogD"] = single_run_log_d(structure)

	return HttpResponse(json.dumps(response_data), content_type="application/json")


def predictLogS(request, structure):
	response_data = {}
	response_data["LogS"] = single_run_log_s(structure)
	return HttpResponse(json.dumps(response_data), content_type="application/json")

def predictLogD(request, structure):
	response_data = {}
	response_data["LogD"] = single_run_log_d(structure)
	return HttpResponse(json.dumps(response_data), content_type="application/json")



def single_run_log_s(structure):

	inchikey = None
	non_exist = False
	property_ = None
	logs = None

	try:
		mol = Chem.MolFromSmiles(structure)
		inchikey = Chem.inchi.MolToInchiKey(mol)
	except:
		inchikey = None

	try:
		property_ = Property.objects.get(inchikey=inchikey, property_name="LogS", source="DeepChem")
	except Exception as e:
		non_exist = True

	if non_exist:
		mol = helper.getMolFromSmiles(structure)
		logs = helper.predictLogS(mol)
		event = Property(inchikey=inchikey, value=logs, property_name="LogS",
									source="DeepChem", create_date=datetime.now())
		event.save()
	
	else:

		logs = float(property_.value)

	return logs


def single_run_log_d(structure):

	inchikey = None
	non_exist = False
	property_ = None
	logd = None

	try:
		mol = Chem.MolFromSmiles(structure)
		inchikey = Chem.inchi.MolToInchiKey(mol)
	except:
		inchikey = None

	try:
		property_ = Property.objects.get(inchikey=inchikey, property_name="LogD", source="DeepChem")
	except Exception as e:
		non_exist = True

	if non_exist:
		mol = helper.getMolFromSmiles(structure)
		logd = helper.predictLogD(mol)
		event = Property(inchikey=inchikey, value=logd, property_name="LogD",
									source="DeepChem", create_date=datetime.now())
		event.save()
	
	else:

		logd = float(property_.value)

	return logd















