from django.shortcuts import render
from django.http import HttpResponse
import json
import os
import pickle
import numpy as np

from metlin.core import getDescriptor
# Create your views here.

model_location = "{0}/metlin/core/{1}".format(os.getcwd(), "metlin_model.pickle")

def predict(request, structure):

	
	

	with open(model_location, "rb") as input_file:
		model = pickle.load(input_file)
	
	fp = getDescriptor.getECFPSmiles(structure)
	x_val = np.asarray([fp], dtype=np.float32)
	rt = model.predict(x_val)


	if len(rt) != 0:
		if len(rt[0]) != 0:
			response_data = {}
			response_data["retention_time"] = str(rt[0][0])

			return HttpResponse(json.dumps(response_data), content_type="application/json")