import json
import os
import sys
import io
import numpy as np
import pandas as pd

# sys.path.append("{0}/deepccs/{1}".format(os.getcwd(),'core/DeepCCS'))
# sys.path.insert(1, 'core')
# sys.path.append('core/DeepCCS')
# sys.path.append('core/DeepCCS/model')

from deepccs.core.model.DeepCCS import DeepCCSModel
from deepccs.core.utils import *

from django.shortcuts import render
from rdkit import Chem
from django.http import HttpResponse


list_adducts = ["M+H","M+Na", "M-H","M-2H"]
model_path   = "{0}/deepccs/saved_models/default/".format(os.getcwd())

def predict(request, structure, adduct):
	response_data = {}
	
	ccs_value = single_run(structure,adduct)
	response_data['deepccs'] = str(ccs_value)

	return HttpResponse(json.dumps(response_data), content_type="application/json")


def single_run(smiles,adducts):
	# only this works, but kind of slow
	model = DeepCCSModel()
	model.load_model_from_file(filename=os.path.join(model_path, "model.h5"),
	                           adduct_encoder_file=os.path.join(model_path, "adducts_encoder.json"),
	                           smiles_encoder_file=os.path.join(model_path, "smiles_encoder.json"))
	ccs_value = None
	try:
		TESTDATA = io.StringIO("""SMILES,Adducts\n{0},{1}""".format(smiles,adducts))
		table = pd.read_csv(TESTDATA, sep=",", header=0)
		table = filter_data(table)
		X_smiles = np.array(table['SMILES'])
		X_adducts = np.array(table['Adducts'])

		ccs_pred = model.predict(X_smiles, X_adducts)
		result   = ccs_pred.flatten()
		ccs_value = result[0]
	except Exception as e:
		print(e)
		ccs_value = 0

	return ccs_value






