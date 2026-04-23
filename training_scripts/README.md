# ChemAPI Model Training Scripts

This directory contains training scripts for all machine learning models used in the ChemAPI project. These scripts have been updated to work with current library versions (TensorFlow 2.16.2, scikit-learn 1.8.0) to avoid version compatibility issues.

## Overview

The ChemAPI project uses several machine learning models:

1. **ChemProp LogS** - Water solubility prediction (scikit-learn RandomForest)
2. **ChemProp LogD** - Distribution coefficient prediction (scikit-learn RandomForest)
3. **METLIN** - Retention time prediction (Keras Neural Network)
4. **DarkChem** - Collision cross section prediction (Variational Autoencoder)
5. **DeepCCS** - CCS prediction from SMILES (Deep CNN)
6. **RapidMiner** - Retention index prediction

## Quick Start

### 1. Prepare Training Data

Create a directory with your training data CSV files:

```bash
mkdir training_data
cd training_data
```

Required CSV files:
- `logs_training_data.csv` - Columns: `SMILES`, `LogS`
- `logd_training_data.csv` - Columns: `SMILES`, `LogD`
- `metlin_training_data.csv` - Columns: `SMILES`, `RetentionTime`

### 2. Retrain All Models

```bash
cd training_scripts
python retrain_all_models.py --all --data-dir ../training_data/
```

### 3. Retrain Specific Models

```bash
# Retrain only ChemProp models
python retrain_all_models.py --models chemprop_logs chemprop_logd --data-dir ../training_data/

# Retrain only METLIN model
python retrain_all_models.py --models metlin --data-dir ../training_data/
```

## Individual Training Scripts

### ChemProp LogS (Water Solubility)

```bash
python train_chemprop_logs.py --data ../training_data/logs_training_data.csv --output ../ChemAPI/chemprop/model/
```

**Data Format:**
```csv
SMILES,LogS
CC(C)O,-0.16
CCO,-0.77
C1=CC=CN=C1,-0.55
```

**Model Details:**
- Algorithm: RandomForestRegressor
- Features: RDKit molecular descriptors (93 features)
- Library: scikit-learn 1.8.0
- Output: `logS.joblib.pkl`

### ChemProp LogD (Distribution Coefficient)

```bash
python train_chemprop_logd.py --data ../training_data/logd_training_data.csv --output ../ChemAPI/chemprop/model/
```

**Data Format:**
```csv
SMILES,LogD
CC(C)O,0.05
CCO,-0.31
C1=CC=CN=C1,0.65
```

**Model Details:**
- Algorithm: RandomForestRegressor
- Features: RDKit molecular descriptors (93 features)
- Library: scikit-learn 1.8.0
- Output: `logD.joblib.pkl`

### METLIN Retention Time

```bash
python train_metlin.py --data ../training_data/metlin_training_data.csv --output ../ChemAPI/metlin/core/
```

**Data Format:**
```csv
SMILES,RetentionTime
CC(C)O,125.3
CCO,98.7
C1=CC=CN=C1,245.6
```

**Model Details:**
- Algorithm: Keras Sequential Neural Network
- Features: ECFP fingerprints (1024 bits)
- Library: TensorFlow 2.16.2
- Output: `metlin_model.keras` (NOT pickle!)

**Important:** After training, update `metlin/views.py` to load the model using:
```python
from tensorflow import keras
model = keras.models.load_model('metlin_model.keras')
```

### DarkChem (Collision Cross Section)

DarkChem uses a Variational Autoencoder that requires more complex data preparation. The training code has been updated for TensorFlow 2.x compatibility.

See `ChemAPI/darkchem/darkchem/training.py` for the updated training functions.

Key changes:
- Import from `tensorflow.keras` instead of `keras`
- `fit_generator()` replaced with `fit()`
- Adam optimizer parameters updated (`lr` → `learning_rate`)

### DeepCCS

DeepCCS model code has been updated for TensorFlow 2.x compatibility.

See `ChemAPI/deepccs/core/model/DeepCCS.py` for the updated model code.

## Training Options

All training scripts support common options:

```bash
--data          Path to training data CSV file (required)
--output        Output directory for trained model
--test-size     Fraction of data for testing (default: 0.2)
--random-seed   Random seed for reproducibility (default: 42)
```

METLIN script also supports:
```bash
--epochs        Maximum training epochs (default: 100)
--batch-size    Training batch size (default: 32)
```

## Model File Formats

### Recommended Formats (Current)

1. **scikit-learn models** → Use `joblib.dump()` and `.joblib.pkl` extension
   ```python
   import joblib
   joblib.dump(model, 'model.joblib.pkl')
   model = joblib.load('model.joblib.pkl')
   ```

2. **Keras/TensorFlow models** → Use `.keras` format or SavedModel
   ```python
   from tensorflow import keras
   model.save('model.keras')  # Recommended
   model = keras.models.load_model('model.keras')
   ```

### Deprecated Formats (Avoid)

❌ **DO NOT USE:**
- `pickle.dump()` for any models
- Old Keras `.h5` format with pickle
- Models saved with different library versions

## Compatibility Updates

The following files have been updated for TensorFlow 2.x / Keras 3 compatibility:

### DarkChem Updates
- `ChemAPI/darkchem/darkchem/training.py`
  - Import from `tensorflow.keras`
  - Replace `fit_generator()` with `fit()`
  
- `ChemAPI/darkchem/darkchem/network.py`
  - Import from `tensorflow.keras`
  - Update Adam optimizer: `lr` → `learning_rate`
  - Remove deprecated `decay` parameter

### DeepCCS Updates
- `ChemAPI/deepccs/core/model/DeepCCS.py`
  - Import from `tensorflow.keras`
  - Update Adam optimizer initialization
  - Fix Model `input` parameter to `inputs`

### View Updates
- `ChemAPI/chemprop/helper.py` - Better error handling for model loading
- `ChemAPI/metlin/views.py` - Added compatibility layer for Keras models

## Troubleshooting

### "ModuleNotFoundError: No module named 'keras.engine'"

**Cause:** Model was saved with old Keras version
**Solution:** Retrain the model with the current TensorFlow version

### "AttributeError: 'RandomForestRegressor' object has no attribute 'estimator'"

**Cause:** scikit-learn model was saved with incompatible version
**Solution:** Retrain the model with current scikit-learn version

### Model Loading Fails

**For Keras models:**
```python
# Use this:
from tensorflow import keras
model = keras.models.load_model('model.keras')

# NOT this:
import pickle
with open('model.pickle', 'rb') as f:
    model = pickle.load(f)
```

**For scikit-learn models:**
```python
# Use this:
import joblib
model = joblib.load('model.joblib.pkl')

# NOT this:
import pickle
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
```

## Example Training Data

### Creating Sample Data

If you don't have training data, you can create sample data for testing:

```python
import pandas as pd
from rdkit import Chem

# Sample SMILES with LogS values
data = {
    'SMILES': [
        'CCO',           # Ethanol
        'CC(C)O',        # Isopropanol
        'C1=CC=CN=C1',   # Pyridine
        'CC(=O)O',       # Acetic acid
        'c1ccccc1',      # Benzene
    ],
    'LogS': [-0.77, -0.16, -0.55, -0.17, -1.47]
}

df = pd.DataFrame(data)
df.to_csv('logs_training_data.csv', index=False)
```

## Testing Your Models

After training, test your models:

```bash
cd ..
python training_scripts/test_api.py
```

This will test all API endpoints including the newly trained models.

## Best Practices

1. **Version Control:** Keep track of which library versions were used
2. **Metadata:** Save training metadata (date, performance metrics, hyperparameters)
3. **Validation:** Always evaluate on a held-out test set
4. **Reproducibility:** Use fixed random seeds
5. **Documentation:** Document your training data sources and preprocessing steps

## Library Versions

Current versions used (as of April 2026):
```
tensorflow==2.16.2
scikit-learn==1.8.0
rdkit==2025.9.3
numpy==1.26.4
pandas==3.0.2
joblib==1.5.3
```

## Additional Resources

- [scikit-learn Model Persistence](https://scikit-learn.org/stable/model_persistence.html)
- [TensorFlow SavedModel Guide](https://www.tensorflow.org/guide/saved_model)
- [RDKit Documentation](https://www.rdkit.org/docs/)
- [Keras Model Saving](https://keras.io/guides/serialization_and_saving/)

## Support

If you encounter issues during training:

1. Check the error messages in the output
2. Verify your training data format
3. Ensure all dependencies are installed
4. Review the MIGRATION_GUIDE.md in the main directory
5. Check that you're using compatible library versions

## License

These training scripts are part of the ChemAPI project. See the main README for license information.
