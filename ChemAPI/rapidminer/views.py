import json

from django.shortcuts import render
from django.http import HttpResponse

from rapidminer.core import retentionIndexPredict

from property_store.models import Property
from rdkit import Chem
from datetime import datetime
# Create your views here.


def predict(request, structure):
	response_data = {}
	retention_index = retentionIndexPredict.single_run(structure)
	response_data['rapidminer'] = str(retention_index)
	return HttpResponse(json.dumps(response_data), content_type="application/json") 



def single_run(structure):
	inchikey = None
	non_exist = True
	property_ = None
	retention_index = None

	try:
		mol = Chem.MolFromSmiles(structure)
		inchikey = Chem.inchi.MolToInchiKey(mol)
	except:
		inchikey = None

	try:
		property_ = Property.objects.get(inchikey=inchikey, property_name="Retenion Index", source="RapidMiner")
		non_exist = False
	except Exception as e:
		non_exist = True


	if non_exist:

		retention_index = retentionIndexPredict.single_run(structure)

		event = Property(inchikey=inchikey, value=retention_index, property_name="Retenion Index",
									source="RapidMiner", create_date=datetime.now())
		event.save()

	else:
		retention_index = float(property_.value)

	return retention_index