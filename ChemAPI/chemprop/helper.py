
import os
import joblib
import numpy as np
from rdkit.ML.Descriptors.MoleculeDescriptors import MolecularDescriptorCalculator
from rdkit import Chem


def getDescriptorName():

	conventionalName = ["LogP", "Molar Refractivity (MR)",
						"Molecular Weight", "Exact Molecular Weight",
						"Heavy Atom Count", "Heavy Atom Molecular Weight",
						"# of NHOH", "# of NO", "# of H Acceptors",
						"# of H Donors", "# of Hetero atoms", "# of Rotatable Bonds",
						"Ring Count", "Polar Surface Area","Solvent-accessible Surface Area"]
	descriptorName = ['MolLogP','MolMR','MolWt','ExactMolWt','HeavyAtomCount','HeavyAtomMolWt','NHOHCount',
	                    'NOCount','NumHAcceptors','NumHDonors','NumHeteroatoms','NumRotatableBonds',
	                    'RingCount','TPSA','LabuteASA']

	return conventionalName, descriptorName

def getDescriptorNamePrediction():
	descriptorName = ['BalabanJ','BertzCT','Ipc','HallKierAlpha','Kappa1',
	                    'Kappa2','Kappa3','Chi0', 'Chi1','Chi0n','Chi1n','Chi2n','Chi3n',
	                    'Chi4n','Chi0v','Chi1v','Chi2v','Chi3v','Chi4v','MolLogP','MolMR',
	                    'MolWt','ExactMolWt','HeavyAtomCount','HeavyAtomMolWt','NHOHCount',
	                    'NOCount','NumHAcceptors','NumHDonors','NumHeteroatoms','NumRotatableBonds',
	                    'NumValenceElectrons','NumAromaticRings','NumSaturatedRings',
	                    'NumAliphaticRings','NumAromaticHeterocycles','NumSaturatedHeterocycles',
	                    'NumAliphaticHeterocycles','NumAromaticCarbocycles','NumSaturatedCarbocycles',
	                    'NumAliphaticCarbocycles','RingCount','FractionCSP3','TPSA','LabuteASA',]
	for i in range(1,15):
	    descriptorName.append('PEOE_VSA{0}'.format(i))
	for i in range(1,11):
	    descriptorName.append('SMR_VSA{0}'.format(i))
	for i in range(1,13):
	    descriptorName.append('SlogP_VSA{0}'.format(i))
	for i in range(1,12):
	    descriptorName.append('EState_VSA{0}'.format(i))
	for i in range(1,11):
	    descriptorName.append('VSA_EState{0}'.format(i))
	    
	return descriptorName

def getMolecularDescriptor(molObject,descriptorName):
	calc = MolecularDescriptorCalculator(descriptorName)
	descrs = calc.CalcDescriptors(molObject)
	return list(descrs)

def getMolFromSmiles(structure):
	mol = Chem.MolFromSmiles(structure)
	return mol


def predictLogS(mol):
	model_location = "{0}/chemprop/model/{1}".format(os.getcwd(), "logS.joblib.pkl")
	clf = joblib.load(model_location)
	v = getMolecularDescriptor(mol,getDescriptorNamePrediction())
	X = np.asarray(v, dtype=np.float32)
	result = clf.predict([X])
	if len(result) == 1:
		result = round(result[0],3)
	return result

def predictLogD(mol):
	model_location = "{0}/chemprop/model/{1}".format(os.getcwd(), "logD.joblib.pkl")
	clf = joblib.load(model_location)
	v = getMolecularDescriptor(mol,getDescriptorNamePrediction())
	X = np.asarray(v, dtype=np.float32)
	result = clf.predict([X])
	if len(result) == 1:
		result = round(result[0],3)
	return result






























