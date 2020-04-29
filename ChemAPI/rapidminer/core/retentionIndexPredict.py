# original paper performance 
# multilinear regression is the best
# r2training set		0.966
# q2cross-validation	0.96
# r2test set			0.949 

import os
import sys

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdMolDescriptors
from rdkit.ML.Descriptors import Descriptors
from rdkit.Chem import MACCSkeys
from rdkit.Chem import Descriptors3D
from rdkit.Chem import Lipinski
from rdkit.Chem.rdPartialCharges import ComputeGasteigerCharges
from rdkit.ML.Descriptors.MoleculeDescriptors import MolecularDescriptorCalculator

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.externals import joblib


# get molObject from smiles
def GetMolFromSmiles(smiles):
	return Chem.MolFromSmiles(smiles)


def GetMolFromInChi(inchi):
	return Chem.inchi.MolFromInchi(inchi)


def GetDescriptorName():
	"""
	Get all descriptor name in list
	Args:
	Returns:
		List
	Raise:
		Exceptions
	"""

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
	# print(len(descriptorName))
	# sys.exit(0)
	return descriptorName


# get desriptor value based on descriptor name
def GetMolecularDescriptor(molObject,descriptorName):
	calc = MolecularDescriptorCalculator(descriptorName)
	descrs = calc.CalcDescriptors(molObject)
	return list(descrs)



def single_run(structure):
	current_dir = os.getcwd() #/Users/xuan/Desktop/retentionCal/ChemAPI/ChemAPI
	reg = joblib.load("{0}/rapidminer/core/rapidminer.joblib.pkl".format(current_dir))
	retention_index = None
	try:
		molObj = GetMolFromSmiles(structure)
		descriptor_name = GetDescriptorName()
		descriptor_value = GetMolecularDescriptor(molObj,descriptor_name)
		predicted_result = reg.predict(np.asarray([descriptor_value], dtype=np.float32))
		retention_index = predicted_result[0]
	except Exception as e:
		retention_index = None


	return retention_index






























































