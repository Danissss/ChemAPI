from rdkit import Chem
from rdkit.Chem import AllChem




def get3Dmol(mol):
	m3 = Chem.AddHs(mol)
	AllChem.EmbedMolecule(m3,randomSeed=0xf00d)
	m3 = Chem.RemoveHs(m3)

	return m3

def inchi2smiles(structure):
	mol = Chem.inchi.MolFromInchi(structure)
	return Chem.MolToSmiles(mol)

def getRDKFingerprint(structure):
	"""
	structure has to be smiles
	"""
	# if "InChI=" in structure:
	# 	structure = inchi2smiles(structure)

	mol = Chem.inchi.MolFromInchi(structure)
	fp = Chem.RDKFingerprint(mol)
	fplist = []
	for i in fp.ToBitString():
		fplist.append(int(i))

	return fplist

def getECFPSmiles(structure):
	
	mol = Chem.MolFromSmiles(structure)
	fp = AllChem.GetMorganFingerprintAsBitVect(mol,2,nBits=1024)

	fplist = []
	for i in fp.ToBitString():
		fplist.append(int(i))

	return fplist

def getECFP(structure):
	mol = Chem.inchi.MolFromInchi(structure)
	fp = AllChem.GetMorganFingerprintAsBitVect(mol,2,nBits=1024)

	fplist = []
	for i in fp.ToBitString():
		fplist.append(int(i))

	return fplist
