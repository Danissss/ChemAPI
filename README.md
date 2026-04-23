# ChemAPI

## Objective/Goal
ChemAPI aims to provide an alternative solution to [ChemAxon](https://chemaxon.com/) for calculating various chemical properties.

## Dependencies
- [RDKit](https://www.rdkit.org/) - Chemistry data storage and calculations
- [Django](https://www.djangoproject.com/) - Web backend framework
- [Django REST Framework](https://www.django-rest-framework.org/) - REST API framework
- MySQL - Data storage
- [TensorFlow/Keras](https://www.tensorflow.org/) - Deep learning models
- [scikit-learn](https://scikit-learn.org/) - Machine learning models
- [OpenBabel](http://openbabel.org/) - Molecular format conversion

## Project Structure

```
ChemAPI/
├── ChemAPI/          # Main Django project
│   ├── chemprop/     # LogS and LogD prediction models
│   ├── darkchem/     # Collision cross section prediction (VAE)
│   ├── deepccs/      # CCS prediction from SMILES
│   ├── metlin/       # Retention time prediction
│   ├── rapidminer/   # Retention index prediction
│   └── ...
├── training_scripts/ # Model training and retraining scripts
└── README.md         # This file
```

## Setup Instructions

### Prerequisites
- Python 3.7+
- MySQL server
- pip or conda package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ChemAPI
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL database**
   ```sql
   CREATE DATABASE chemapi;
   CREATE USER 'chemapi'@'localhost' IDENTIFIED BY 'chemapi';
   GRANT ALL PRIVILEGES ON chemapi.* TO 'chemapi'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Update database settings** in `ChemAPI/settings.py` if needed

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Running the Application

### Development Server
```bash
python manage.py runserver
```
The API will be available at `http://localhost:8000/`

### Production with Gunicorn
```bash
PYTHONPATH=$(pwd) gunicorn --bind 127.0.0.1:8000 ChemAPI.wsgi:application
```

### Running Tests
```bash
python manage.py test
```

### Deployment Check
```bash
python manage.py check --deploy
```

## API Usage

All endpoints accept POST requests with JSON body for better handling of chemical structures with special characters. Legacy GET requests with path parameters are still supported.

### ChemProp - Chemical Properties Prediction

**Predict All Properties (LogS, LogD, and molecular descriptors)**
```bash
# POST request (recommended)
curl -X POST http://localhost:8000/chemprop/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1"}'

# Legacy GET request
curl http://localhost:8000/chemprop/predict/C1=CC=CN=C1/
```

**Predict LogS (Water Solubility)**
```bash
curl -X POST http://localhost:8000/chemprop/predict/logs/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1"}'
```

**Predict LogD (Distribution Coefficient)**
```bash
curl -X POST http://localhost:8000/chemprop/predict/logd/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1"}'
```

### DarkChem - Collision Cross Section Prediction

**Predict CCS with different adducts**
```bash
# Protonated [M+H]+
curl -X POST http://localhost:8000/darkchem/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1", "adduct": "[M+H]+"}'

# Deprotonated [M-H]-
curl -X POST http://localhost:8000/darkchem/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1", "adduct": "[M-H]-"}'

# Sodiated [M+Na]+
curl -X POST http://localhost:8000/darkchem/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1", "adduct": "[M+Na]+"}'
```

**Valid adduct types**: `[M+H]+`, `[M-H]-`, `[M+Na]+`

### METLIN - Retention Time Prediction

```bash
curl -X POST http://localhost:8000/metlin/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1"}'
```

### RapidMiner - Retention Index Prediction

```bash
curl -X POST http://localhost:8000/rapidminer/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1"}'
```

### Input Formats

- **SMILES**: The primary input format for chemical structures (e.g., `C1=CC=CN=C1` for pyridine)
- **JSON body keys**: Use either `"structure"` or `"smiles"` in the JSON body

### Error Handling

The API returns proper HTTP status codes:
- `200 OK`: Successful prediction
- `400 Bad Request`: Invalid input (missing structure, invalid JSON, or invalid adduct type)
- `500 Internal Server Error`: Prediction or model loading failure

Error responses include an `"error"` field with a descriptive message.

## Troubleshooting

### Model Compatibility Issues

If you encounter errors like:
- `ModuleNotFoundError: No module named 'keras.engine'`
- `AttributeError: 'RandomForestRegressor' object has no attribute 'estimator'`

These indicate that the pre-trained models were saved with older versions of TensorFlow/Keras or scikit-learn and are incompatible with current versions. You'll need to:

1. **Retrain the models** with the current library versions (recommended), or
2. **Downgrade the dependencies** to match the versions used during model training (not recommended)

#### Quick Retraining Guide

```bash
# Generate sample training data (for testing)
cd training_scripts
python generate_sample_data.py --output ./sample_data/

# Retrain all models
python retrain_all_models.py --all --data-dir ./sample_data/

# Or retrain specific models
python train_chemprop_logs.py --data ./sample_data/logs_training_data.csv
python train_chemprop_logd.py --data ./sample_data/logd_training_data.csv
python train_metlin.py --data ./sample_data/metlin_training_data.csv
```

See [training_scripts/README.md](training_scripts/README.md) for detailed training instructions and [TRAINING_UPDATES.md](TRAINING_UPDATES.md) for information about compatibility updates.

### URL Encoding Issues

If you need to use GET requests with complex chemical structures, properly encode special characters:
```bash
# Bad (will fail with brackets and special chars)
curl http://localhost:8000/darkchem/predict/C1=CC=CN=C1/[M+H]+

# Good (use POST with JSON instead)
curl -X POST http://localhost:8000/darkchem/predict/ \
  -H "Content-Type: application/json" \
  -d '{"structure": "C1=CC=CN=C1", "adduct": "[M+H]+"}'
```

## Publications Referenced
- [DarkChem](https://pubs.acs.org/doi/abs/10.1021/acs.analchem.9b02348) - Collision cross section prediction
- [DeepCCS](https://pubs.acs.org/doi/abs/10.1021/acs.analchem.8b05821) - Deep learning for CCS prediction
- [METLIN](https://www.nature.com/articles/s41467-019-13680-7) - Metabolomics database and tools

## Lint

```bash
pip install pylint
pylint $(find . -name "*.py")

pip install autopep8 black flake8
autopep8 --in-place --aggressive --aggressive $(find . -name "*.py")
black .
flake8 .
```

## Updating Dependencies

Here are the best ways to update dependencies:

### **1. Check Current Versions**
```bash
pip list
```
Shows all installed packages and their current versions.

### **2. Check for Outdated Packages**
```bash
pip list --outdated
```
Shows which packages have newer versions available.

### **3. Update Individual Package**
```bash
pip install --upgrade package_name
# or
pip install -U package_name
```

### **4. Update requirements.txt After Installing**
Once you've tested updates locally, update the file:
```bash
pip freeze > requirements.txt
```
This exports all installed packages with their current versions.

### **5. Safe Update Strategy** (Recommended)
1. Update one dependency at a time and test
2. Check compatibility with other packages
3. Update the version in requirements.txt manually:
   ```
   # Before
   Django==2.2.28
   
   # After
   Django==3.2.13
   ```
4. Run tests to ensure everything works
5. Commit changes

**Note**: When updating machine learning libraries (TensorFlow, Keras, scikit-learn), you may need to retrain and save models with the new versions to avoid compatibility issues.
