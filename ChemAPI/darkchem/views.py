import json
import os
from django.shortcuts import render
from django.http import HttpResponse
import gc

# import darkchem
from .darkchem import predict
from pandas import DataFrame as df

# Create your views here.

# from openbabel import pybel 

adduct_map = {"M+H": "protonated", "M−H": "deprotonated", "M+Na": "sodiated"}

def predicts(requests, structure, adduct):

	response_data = {}


	model = adduct_map[adduct]
	# smiles = pybel.readstring('smi', structure).write('can').strip()
	model_location = "{0}/darkchem/darkchem/{1}".format(os.getcwd(), model)

	# adduct_map = {"[M+H]+": "protonated", "[M−H]−": "deprotonated", "[M+Na]": "sodiated"}
	

	if adduct not in adduct_map.keys():
		response_data["error"] = "Adduct type not valid. (M+H, M−H, M+Na are valid options)"
		return HttpResponse(json.dumps(response_data), content_type="application/json")
		
	

	properties = predict.properties(structure, model_location)

	ccs_value = {}
	for i in range(properties.shape[-1]):
		if i == 0:
			ccs_value["m/z"] = properties[:, i].tolist()
		elif i == 1:
			ccs_value["css"] = properties[:, i].tolist()

	response_data['darkchem'] = ccs_value
	
	gc.collect()

	return HttpResponse(json.dumps(response_data), content_type="application/json")




























