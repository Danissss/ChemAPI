from django.shortcuts import render
from django.http import HttpResponse
import json
import os
import pickle
import numpy as np
import gc

from metlin.core import getDescriptor

from property_store.models import Property
from rdkit import Chem
from datetime import datetime
# Create your views here.

model_location = "{0}/metlin/core/{1}".format(os.getcwd(), "metlin_model.pickle")

def predict(request, structure):

	response_data={}
	retention_time = single_run(structure)
	response_data['retention_time'] = str(retention_time)

	gc.collect()
	
	return HttpResponse(json.dumps(response_data), content_type="application/json")


def single_run(structure):
	inchikey = None
	non_exist = True
	property_ = None
	retention_time = None

	try:
		mol = Chem.MolFromSmiles(structure)
		inchikey = Chem.inchi.MolToInchiKey(mol)
	except:
		inchikey = None

	try:
		property_ = Property.objects.get(inchikey=inchikey, property_name="Retenion Time", source="METLIN")
		non_exist = False
	except Exception as e:
		non_exist = True


	if non_exist:

		with open(model_location, "rb") as input_file:
			model = pickle.load(input_file)
		
		fp = getDescriptor.getECFPSmiles(structure)
		x_val = np.asarray([fp], dtype=np.float32)
		rt = model.predict(x_val)

		response_data = {}

		if len(rt) != 0:
			if len(rt[0]) != 0:
				
				retention_time = rt[0][0]

				event = Property(inchikey=inchikey, value=retention_time, property_name="Retenion Time",
									source="METLIN", create_date=datetime.now())
				event.save()
	else:
		retention_time = float(property_.value)

	return retention_time






