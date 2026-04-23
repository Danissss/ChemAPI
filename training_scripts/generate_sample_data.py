#!/usr/bin/env python3
"""
Generate sample training data for testing the ChemAPI model training scripts

This script creates sample CSV files with synthetic data for testing purposes.
DO NOT use this data for production models - it's only for testing the training pipeline.

Usage:
    python generate_sample_data.py --output ./sample_training_data/
"""

import argparse
import os
import random
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen


# Sample SMILES strings from different chemical classes
SAMPLE_SMILES = [
    # Alcohols
    'CCO', 'CC(C)O', 'CCCO', 'CC(C)CO', 'CCCCO',
    # Aromatics
    'c1ccccc1', 'c1ccc(C)cc1', 'c1ccc(O)cc1', 'c1ccc(N)cc1',
    # Heterocycles
    'C1=CC=CN=C1', 'c1ccncc1', 'c1cccnc1', 'c1cnccn1',
    # Carboxylic acids
    'CC(=O)O', 'CCC(=O)O', 'CCCC(=O)O',
    # Amines
    'CCN', 'CC(C)N', 'CCCN',
    # Ethers
    'COC', 'CCOC', 'CCOCC',
    # Ketones
    'CC(=O)C', 'CCC(=O)C', 'CC(=O)CC',
    # Esters
    'CC(=O)OC', 'CCC(=O)OC', 'CC(=O)OCC',
    # Halogenated
    'CCCl', 'CCBr', 'CCF',
    # Complex molecules
    'CC(C)Cc1ccc(cc1)C(C)C(=O)O',  # Ibuprofen
    'CC(=O)Oc1ccccc1C(=O)O',        # Aspirin
    'CN1C=NC2=C1C(=O)N(C(=O)N2C)C', # Caffeine
]


def calculate_logs(mol):
    """Calculate approximate LogS using RDKit properties"""
    if mol is None:
        return None
    
    # Very rough approximation based on LogP and molecular weight
    logp = Crippen.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    
    # Rough formula (not accurate, just for testing)
    logs = -0.5 * logp - 0.01 * (mw - 100) + random.gauss(0, 0.2)
    return round(logs, 2)


def calculate_logd(mol):
    """Calculate approximate LogD using RDKit properties"""
    if mol is None:
        return None
    
    # LogD is similar to LogP at neutral pH
    logp = Crippen.MolLogP(mol)
    
    # Add some variation
    logd = logp + random.gauss(0, 0.3)
    return round(logd, 2)


def calculate_retention_time(mol):
    """Calculate synthetic retention time based on molecular properties"""
    if mol is None:
        return None
    
    # Based on molecular weight and LogP
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    
    # Synthetic formula
    rt = 50 + 20 * logp + 0.5 * mw + random.gauss(0, 10)
    return round(max(10, rt), 1)


def generate_logs_data(smiles_list, output_dir):
    """Generate LogS training data"""
    data = []
    
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            logs = calculate_logs(mol)
            if logs is not None:
                data.append({'SMILES': smiles, 'LogS': logs})
    
    df = pd.DataFrame(data)
    output_path = os.path.join(output_dir, 'logs_training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated LogS data: {output_path} ({len(df)} samples)")
    
    return output_path


def generate_logd_data(smiles_list, output_dir):
    """Generate LogD training data"""
    data = []
    
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            logd = calculate_logd(mol)
            if logd is not None:
                data.append({'SMILES': smiles, 'LogD': logd})
    
    df = pd.DataFrame(data)
    output_path = os.path.join(output_dir, 'logd_training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated LogD data: {output_path} ({len(df)} samples)")
    
    return output_path


def generate_metlin_data(smiles_list, output_dir):
    """Generate METLIN retention time data"""
    data = []
    
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            rt = calculate_retention_time(mol)
            if rt is not None:
                data.append({'SMILES': smiles, 'RetentionTime': rt})
    
    df = pd.DataFrame(data)
    output_path = os.path.join(output_dir, 'metlin_training_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated METLIN data: {output_path} ({len(df)} samples)")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample training data for ChemAPI models'
    )
    parser.add_argument('--output', default='./sample_training_data/',
                        help='Output directory for generated data files')
    parser.add_argument('--samples', type=int, default=None,
                        help='Number of samples (default: use all sample SMILES)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Select SMILES
    if args.samples:
        smiles_list = random.sample(SAMPLE_SMILES, min(args.samples, len(SAMPLE_SMILES)))
    else:
        smiles_list = SAMPLE_SMILES
    
    print("="*60)
    print("Generating Sample Training Data")
    print("="*60)
    print(f"Output directory: {args.output}")
    print(f"Number of samples: {len(smiles_list)}")
    print()
    print("WARNING: This data is synthetic and for testing only!")
    print("DO NOT use for production models.")
    print("="*60)
    print()
    
    # Generate data files
    generate_logs_data(smiles_list, args.output)
    generate_logd_data(smiles_list, args.output)
    generate_metlin_data(smiles_list, args.output)
    
    print()
    print("="*60)
    print("Sample data generation complete!")
    print("="*60)
    print()
    print("Next steps:")
    print(f"1. Review the generated files in {args.output}")
    print("2. Run training scripts with this sample data:")
    print(f"   python retrain_all_models.py --all --data-dir {args.output}")
    print()
    print("Remember: This is test data only! For production, use real experimental data.")


if __name__ == '__main__':
    main()
