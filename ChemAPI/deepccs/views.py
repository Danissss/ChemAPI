import json
import os
import io
import numpy as np
import pandas as pd
import gc

from deepccs.core.model.DeepCCS import DeepCCSModel
from deepccs.core.utils import filter_data

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# check if the propery is already calculated
# it's faster than run deep learning algorithm everytime
from property_store.models import Property
from rdkit import Chem
from datetime import datetime

list_adducts = ["M+H", "M+Na", "M-H", "M-2H"]
model_path = "{0}/deepccs/saved_models/default/".format(os.getcwd())


@csrf_exempt
def predict(request, structure=None, adduct=None):
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
            "Adduct is required. Valid options: M+H, M+Na, M-H, M-2H"
        )
        return JsonResponse(response_data, status=400)

    if adduct not in list_adducts:
        response_data["error"] = f"Invalid adduct type. Valid options: {
            ', '.join(list_adducts)}"
        return JsonResponse(response_data, status=400)

    try:
        ccs_value = single_run(structure, adduct)
        response_data["deepccs"] = str(ccs_value)
    except Exception as e:
        response_data["error"] = f"Prediction failed: {str(e)}"
        return JsonResponse(response_data, status=500)

    gc.collect()

    return JsonResponse(response_data)


def single_run(smiles, adducts):

    inchikey = None
    non_exist = True
    property_ = None
    ccs_value = None

    try:
        mol = Chem.MolFromSmiles(smiles)
        inchikey = Chem.inchi.MolToInchiKey(mol)
    except BaseException:
        # couldn't produce inchikey for structure failed
        inchikey = None

    try:
        # try to get this structure with this adduct predicted by deepccs
        property_ = Property.objects.get(
            inchikey=inchikey,
            property_name="CCS{0}".format(adducts),
            source="DeepCCS")
        non_exist = False
    except Exception:
        non_exist = True

    if non_exist:
        # only this works, but kind of slow
        model = DeepCCSModel()
        model.load_model_from_file(
            filename=os.path.join(model_path, "model.h5"),
            adduct_encoder_file=os.path.join(
                model_path, "adducts_encoder.json"),
            smiles_encoder_file=os.path.join(
                model_path, "smiles_encoder.json"),
        )
        try:
            TESTDATA = io.StringIO(
                """SMILES,Adducts\n{0},{1}""".format(smiles, adducts)
            )
            table = pd.read_csv(TESTDATA, sep=",", header=0)
            table = filter_data(table)
            X_smiles = np.array(table["SMILES"])
            X_adducts = np.array(table["Adducts"])

            ccs_pred = model.predict(X_smiles, X_adducts)
            result = ccs_pred.flatten()
            ccs_value = result[0]
        except Exception:
            ccs_value = 0

        ccs_value_item = ccs_value.item()
        event = Property(
            inchikey=inchikey,
            value=ccs_value_item,
            property_name="CCS{0}".format(adducts),
            source="DeepCCS",
            create_date=datetime.now(),
        )
        event.save()
    else:
        ccs_value = float(property_.value)

    return round(ccs_value, 2)
