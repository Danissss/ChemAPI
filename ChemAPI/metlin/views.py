from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import pickle
import sys
import numpy as np
import gc

from metlin.core import getDescriptor

from property_store.models import Property
from rdkit import Chem
from datetime import datetime

# Create your views here.

model_location = "{0}/metlin/core/{1}".format(
    os.getcwd(), "metlin_model.pickle")


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
        retention_time = single_run(structure)
        response_data["retention_time"] = str(retention_time)
    except Exception as e:
        response_data["error"] = f"Prediction failed: {str(e)}"
        return JsonResponse(response_data, status=500)

    gc.collect()

    return JsonResponse(response_data)


def single_run(structure):
    inchikey = None
    non_exist = True
    property_ = None
    retention_time = None

    try:
        mol = Chem.MolFromSmiles(structure)
        inchikey = Chem.inchi.MolToInchiKey(mol)
    except BaseException:
        inchikey = None

    try:
        property_ = Property.objects.get(
            inchikey=inchikey, property_name="Retenion Time", source="METLIN"
        )
        non_exist = False
    except Exception:
        non_exist = True

    if non_exist:
        try:
            # Try to load with keras compatibility
            import tensorflow as tf

            # Register keras.engine as keras.src.engine for backward
            # compatibility
            if not hasattr(sys.modules, "keras.engine"):
                try:
                    import keras.src.engine

                    sys.modules["keras.engine"] = keras.src.engine
                except BaseException:
                    pass

            with open(model_location, "rb") as input_file:
                model = pickle.load(input_file)
        except ModuleNotFoundError as e:
            raise Exception(
                f"Model compatibility error: {
                    str(e)}. The model needs to be retrained with current TensorFlow/Keras version.")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")

        fp = getDescriptor.getECFPSmiles(structure)
        x_val = np.asarray([fp], dtype=np.float32)
        rt = model.predict(x_val)

        if len(rt) != 0:
            if len(rt[0]) != 0:

                retention_time = rt[0][0]

                event = Property(
                    inchikey=inchikey,
                    value=retention_time,
                    property_name="Retenion Time",
                    source="METLIN",
                    create_date=datetime.now(),
                )
                event.save()
    else:
        retention_time = float(property_.value)

    return retention_time
