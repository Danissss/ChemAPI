#!/usr/bin/env python3
"""
Training script for ChemProp LogD (Distribution Coefficient) prediction model
Uses scikit-learn RandomForestRegressor with molecular descriptors from RDKit

Requirements:
- Training data CSV with columns: 'SMILES', 'LogD'
- RDKit for molecular descriptor calculation
- scikit-learn for model training

Usage:
    python train_chemprop_logd.py --data training_data.csv --output ../ChemAPI/chemprop/model/
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

# Add parent directory to path to import helper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ChemAPI'))

from chemprop import helper
from rdkit import Chem
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def load_data(data_file):
    """Load training data from CSV file"""
    print(f"Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    
    if 'SMILES' not in df.columns or 'LogD' not in df.columns:
        raise ValueError("CSV must contain 'SMILES' and 'LogD' columns")
    
    return df


def calculate_descriptors(smiles_list):
    """Calculate molecular descriptors for a list of SMILES strings"""
    print("Calculating molecular descriptors...")
    descriptor_names = helper.getDescriptorNamePrediction()
    descriptors = []
    valid_indices = []
    
    for i, smiles in enumerate(smiles_list):
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                desc = helper.getMolecularDescriptor(mol, descriptor_names)
                descriptors.append(desc)
                valid_indices.append(i)
            else:
                print(f"Warning: Invalid SMILES at index {i}: {smiles}")
        except Exception as e:
            print(f"Warning: Error processing SMILES at index {i}: {smiles} - {str(e)}")
    
    return np.array(descriptors, dtype=np.float32), valid_indices


def train_model(X_train, y_train, X_test, y_test):
    """Train RandomForestRegressor model"""
    print("Training RandomForestRegressor...")
    
    # Initialize model with optimized hyperparameters
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=30,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate on training set
    train_pred = model.predict(X_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    train_mae = mean_absolute_error(y_train, train_pred)
    train_r2 = r2_score(y_train, train_pred)
    
    print(f"\nTraining Set Performance:")
    print(f"  RMSE: {train_rmse:.4f}")
    print(f"  MAE:  {train_mae:.4f}")
    print(f"  R²:   {train_r2:.4f}")
    
    # Evaluate on test set
    test_pred = model.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    test_mae = mean_absolute_error(y_test, test_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"\nTest Set Performance:")
    print(f"  RMSE: {test_rmse:.4f}")
    print(f"  MAE:  {test_mae:.4f}")
    print(f"  R²:   {test_r2:.4f}")
    
    return model, {
        'train_rmse': train_rmse,
        'train_mae': train_mae,
        'train_r2': train_r2,
        'test_rmse': test_rmse,
        'test_mae': test_mae,
        'test_r2': test_r2
    }


def save_model(model, metrics, output_dir):
    """Save model using joblib"""
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, 'logD.joblib.pkl')
    print(f"\nSaving model to {model_path}...")
    joblib.dump(model, model_path)
    
    # Save metadata
    metadata_path = os.path.join(output_dir, 'logD_metadata.txt')
    with open(metadata_path, 'w') as f:
        f.write(f"LogD Model Training Metadata\n")
        f.write(f"Trained: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model type: RandomForestRegressor\n")
        f.write(f"Scikit-learn version: {joblib.__version__}\n")
        f.write(f"\nPerformance Metrics:\n")
        for key, value in metrics.items():
            f.write(f"  {key}: {value:.4f}\n")
    
    print(f"Model saved successfully!")
    print(f"Metadata saved to {metadata_path}")


def main():
    parser = argparse.ArgumentParser(description='Train LogD prediction model')
    parser.add_argument('--data', required=True, help='Path to training data CSV file')
    parser.add_argument('--output', default='../ChemAPI/chemprop/model/', 
                        help='Output directory for trained model')
    parser.add_argument('--test-size', type=float, default=0.2, 
                        help='Fraction of data to use for testing (default: 0.2)')
    parser.add_argument('--random-seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("LogD Model Training")
    print("="*60)
    
    # Load data
    df = load_data(args.data)
    print(f"Loaded {len(df)} samples")
    
    # Calculate descriptors
    X, valid_indices = calculate_descriptors(df['SMILES'].tolist())
    y = df['LogD'].iloc[valid_indices].values
    
    print(f"Successfully calculated descriptors for {len(X)} samples")
    print(f"Number of features: {X.shape[1]}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_seed
    )
    
    print(f"\nData split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Testing samples:  {len(X_test)}")
    
    # Train model
    model, metrics = train_model(X_train, y_train, X_test, y_test)
    
    # Save model
    save_model(model, metrics, args.output)
    
    print("\n" + "="*60)
    print("Training completed successfully!")
    print("="*60)


if __name__ == '__main__':
    main()
