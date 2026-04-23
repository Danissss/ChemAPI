import json
import gc

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rapidminer.core import retentionIndexPredict

from property_store.models import Property
from rdkit import Chem
from datetime import datetime

# Create your views here.


@csrf_exempt
def predict(request, structure=None):
    response_data = {}

    # Handle POST request with JSON body
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            structure = data.get("structure") or data.get("smiles")
        except json.JSONDecodeError:
            response_data["error"] = "Invalid JSON body"
            return JsonResponse(response_data, status=400)

    # Validate input
    if not structure:
        response_data["error"] = (
            'Structure/SMILES is required. Use POST with JSON body: '
            '{"structure": "C1=CC=CN=C1"}'
        )
        return JsonResponse(response_data, status=400)

    try:
        retention_index = retentionIndexPredict.single_run(structure)
        response_data["rapidminer"] = str(retention_index)
    except Exception as e:
        response_data["error"] = f"Prediction failed: {str(e)}"
        return JsonResponse(response_data, status=500)

    gc.collect()

    return JsonResponse(response_data)


def single_run(structure):
    inchikey = None
    non_exist = True
    property_ = None
    retention_index = None

    try:
        mol = Chem.MolFromSmiles(structure)
        inchikey = Chem.inchi.MolToInchiKey(mol)
    except BaseException:
        inchikey = None

    try:
        property_ = Property.objects.get(
            inchikey=inchikey,
            property_name="Retenion Index",
            source="RapidMiner")
        non_exist = False
    except Exception:
        non_exist = True

    if non_exist:

        retention_index = retentionIndexPredict.single_run(structure)

        event = Property(
            inchikey=inchikey,
            value=retention_index,
            property_name="Retenion Index",
            source="RapidMiner",
            create_date=datetime.now(),
        )
        event.save()

    else:
        retention_index = float(property_.value)

    return retention_index
