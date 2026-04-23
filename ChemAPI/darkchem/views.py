import json
import os
import gc
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .darkchem import predict

# Create your views here.

# from openbabel import pybel

adduct_map = {
    "M+H": "protonated",
    "[M+H]+": "protonated",
    "M−H": "deprotonated",
    "[M-H]-": "deprotonated",
    "[M−H]−": "deprotonated",
    "M+Na": "sodiated",
    "[M+Na]+": "sodiated",
}


@csrf_exempt
def predicts(request, structure=None, adduct=None):
    response_data = {}

    # Handle POST request with JSON body
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            structure = data.get("structure") or data.get("smiles")
            adduct = data.get("adduct")
        except json.JSONDecodeError:
            response_data["error"] = "Invalid JSON body"
            return JsonResponse(response_data, status=400)

    # Validate inputs
    if not structure:
        response_data["error"] = (
            'Structure/SMILES is required. Use POST with JSON body: '
            '{"structure": "C1=CC=CN=C1", "adduct": "[M+H]+"}'
        )
        return JsonResponse(response_data, status=400)

    if not adduct:
        response_data["error"] = (
            "Adduct is required. Valid options: [M+H]+, [M-H]-, [M+Na]+"
        )
        return JsonResponse(response_data, status=400)

    # Normalize adduct to internal format
    if adduct not in adduct_map.keys():
        response_data["error"] = (
            "Adduct type not valid. Valid options: [M+H]+, [M-H]-, [M+Na]+"
        )
        return JsonResponse(response_data, status=400)

    model = adduct_map[adduct]
    model_location = "{0}/darkchem/darkchem/{1}".format(os.getcwd(), model)

    try:
        properties = predict.properties(structure, model_location)

        ccs_value = {}
        for i in range(properties.shape[-1]):
            if i == 0:
                ccs_value["m/z"] = properties[:, i].tolist()
            elif i == 1:
                ccs_value["css"] = properties[:, i].tolist()

        response_data["darkchem"] = ccs_value
    except Exception as e:
        response_data["error"] = f"Prediction failed: {str(e)}"
        return JsonResponse(response_data, status=500)

    gc.collect()

    return JsonResponse(response_data)
