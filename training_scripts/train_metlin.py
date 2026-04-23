#!/usr/bin/env python3
"""
Training script for METLIN Retention Time prediction model
Uses Keras/TensorFlow neural network with molecular fingerprints from RDKit

Requirements:
- Training data CSV with columns: 'SMILES', 'RetentionTime'
- RDKit for molecular fingerprint calculation
- TensorFlow/Keras for model training

Usage:
    python train_metlin.py --data training_data.csv --output ../ChemAPI/metlin/core/
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add parent directory to path to import getDescriptor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ChemAPI'))

from metlin.core import getDescriptor
from rdkit import Chem
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def load_data(data_file):
    """Load training data from CSV file"""
    print(f"Loading data from {data_file}...")
    df = pd.read_csv(data_file)
    
    if 'SMILES' not in df.columns or 'RetentionTime' not in df.columns:
        raise ValueError("CSV must contain 'SMILES' and 'RetentionTime' columns")
    
    return df


def calculate_fingerprints(smiles_list):
    """Calculate ECFP molecular fingerprints for a list of SMILES strings"""
    print("Calculating molecular fingerprints...")
    fingerprints = []
    valid_indices = []
    
    for i, smiles in enumerate(smiles_list):
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                fp = getDescriptor.getECFPSmiles(smiles)
                fingerprints.append(fp)
                valid_indices.append(i)
            else:
                print(f"Warning: Invalid SMILES at index {i}: {smiles}")
        except Exception as e:
            print(f"Warning: Error processing SMILES at index {i}: {smiles} - {str(e)}")
    
    return np.array(fingerprints, dtype=np.float32), valid_indices


def create_model(input_dim):
    """Create Keras neural network model"""
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='linear')
    ])
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    
    return model


def train_model(X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
    """Train Keras neural network model"""
    print("Training Keras neural network...")
    
    # Create model
    model = create_model(X_train.shape[1])
    
    # Print model summary
    model.summary()
    
    # Define callbacks
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-6,
        verbose=1
    )
    
    # Train the model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
    
    # Evaluate on training set
    train_pred = model.predict(X_train, verbose=0)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    train_mae = mean_absolute_error(y_train, train_pred)
    train_r2 = r2_score(y_train, train_pred)
    
    print(f"\nTraining Set Performance:")
    print(f"  RMSE: {train_rmse:.4f}")
    print(f"  MAE:  {train_mae:.4f}")
    print(f"  R²:   {train_r2:.4f}")
    
    # Evaluate on validation set
    val_pred = model.predict(X_val, verbose=0)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
    val_mae = mean_absolute_error(y_val, val_pred)
    val_r2 = r2_score(y_val, val_pred)
    
    print(f"\nValidation Set Performance:")
    print(f"  RMSE: {val_rmse:.4f}")
    print(f"  MAE:  {val_mae:.4f}")
    print(f"  R²:   {val_r2:.4f}")
    
    return model, history, {
        'train_rmse': train_rmse,
        'train_mae': train_mae,
        'train_r2': train_r2,
        'val_rmse': val_rmse,
        'val_mae': val_mae,
        'val_r2': val_r2
    }


def save_model(model, metrics, output_dir):
    """Save model in Keras format (recommended over pickle)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save in Keras format (not pickle!)
    model_path = os.path.join(output_dir, 'metlin_model.keras')
    print(f"\nSaving model to {model_path}...")
    model.save(model_path)
    
    # Also save in SavedModel format for compatibility
    savedmodel_path = os.path.join(output_dir, 'metlin_model')
    model.save(savedmodel_path, save_format='tf')
    print(f"SavedModel format saved to {savedmodel_path}/")
    
    # Save metadata
    metadata_path = os.path.join(output_dir, 'metlin_model_metadata.txt')
    with open(metadata_path, 'w') as f:
        f.write(f"METLIN Retention Time Model Training Metadata\n")
        f.write(f"Trained: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model type: Keras Sequential Neural Network\n")
        f.write(f"TensorFlow version: {keras.__version__}\n")
        f.write(f"Input: ECFP fingerprints (1024 bits)\n")
        f.write(f"\nPerformance Metrics:\n")
        for key, value in metrics.items():
            f.write(f"  {key}: {value:.4f}\n")
        f.write(f"\nNote: Model saved in .keras format (not pickle)\n")
        f.write(f"Load with: model = keras.models.load_model('metlin_model.keras')\n")
    
    print(f"Model saved successfully!")
    print(f"Metadata saved to {metadata_path}")
    print(f"\nIMPORTANT: Update views.py to use keras.models.load_model() instead of pickle.load()")


def main():
    parser = argparse.ArgumentParser(description='Train METLIN retention time prediction model')
    parser.add_argument('--data', required=True, help='Path to training data CSV file')
    parser.add_argument('--output', default='../ChemAPI/metlin/core/', 
                        help='Output directory for trained model')
    parser.add_argument('--test-size', type=float, default=0.2, 
                        help='Fraction of data to use for validation (default: 0.2)')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Maximum number of training epochs (default: 100)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training (default: 32)')
    parser.add_argument('--random-seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("METLIN Retention Time Model Training")
    print("="*60)
    
    # Load data
    df = load_data(args.data)
    print(f"Loaded {len(df)} samples")
    
    # Calculate fingerprints
    X, valid_indices = calculate_fingerprints(df['SMILES'].tolist())
    y = df['RetentionTime'].iloc[valid_indices].values
    
    print(f"Successfully calculated fingerprints for {len(X)} samples")
    print(f"Fingerprint size: {X.shape[1]}")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_seed
    )
    
    print(f"\nData split:")
    print(f"  Training samples:   {len(X_train)}")
    print(f"  Validation samples: {len(X_val)}")
    
    # Train model
    model, history, metrics = train_model(
        X_train, y_train, X_val, y_val,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
    
    # Save model
    save_model(model, metrics, args.output)
    
    print("\n" + "="*60)
    print("Training completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update metlin/views.py to load the model with:")
    print("   from tensorflow import keras")
    print("   model = keras.models.load_model('metlin_model.keras')")
    print("2. Remove the old pickle loading code")


if __name__ == '__main__':
    main()
