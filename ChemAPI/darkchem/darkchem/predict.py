from . import preprocess
from . import utils
from os.path import *
import numpy as np


def latent(smiles, network):
    # convert smiles
    vectors = np.vstack(preprocess.vectorize(smiles))

    # load model
    config = utils.load_config(join(network, 'arguments.txt'))
    config['output'] = network
    model = utils.model_from_config(config)

    # predict latent
    latent = model.encoder.predict(vectors)

    # overwrite invalids
    latent = np.where(np.all(vectors == 0, axis=1, keepdims=True), np.nan, latent)

    return latent


def properties(smiles, network):
    # convert smiles
    vectors = np.vstack(preprocess.vectorize(smiles))

    # load model
    # network is the directory that contains all the model and arguments.txt
    config = utils.load_config(join(network, 'arguments.txt'))
    # print(config)
    config['output'] = network
    model = utils.model_from_config(config)

    # predict latent
    latent = model.encoder.predict(vectors)
    # print(latent)

    # properties
    properties = model.predictor.predict(latent)
    
    # overwrite invalids
    properties = np.where(np.all(vectors == 0, axis=1, keepdims=True), np.nan, properties)
    # print(properties)
    return properties


def softmax(smiles, network):
    # convert smiles
    vectors = np.vstack(preprocess.vectorize(smiles))

    # load model
    config = utils.load_config(join(network, 'arguments.txt'))
    config['output'] = network
    model = utils.model_from_config(config)

    # predict latent
    latent = model.encoder.predict(vectors)

    # softmax
    softmax = model.decoder.predict(latent)

    # argmax and convert to smiles
    smiles_out = np.array([utils.vec2struct(x) for x in np.argmax(softmax, axis=-1)])

    # overwrite invalids
    idx = np.where(np.all(vectors == 0, axis=1))[0]
    smiles_out[idx] = np.nan
    softmax[idx, :, :] = np.nan

    return softmax, smiles_out
