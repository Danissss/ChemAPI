#!/usr/bin/env python3
"""
Master retraining script for all ChemAPI models

This script provides a unified interface to retrain all models in the ChemAPI project.
It checks for available training data and retrains models as needed.

Usage:
    # Retrain all models
    python retrain_all_models.py --all --data-dir ./training_data/
    
    # Retrain specific models
    python retrain_all_models.py --models chemprop metlin --data-dir ./training_data/
    
    # Dry run to see what would be trained
    python retrain_all_models.py --all --data-dir ./training_data/ --dry-run
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path


# Model definitions with their training scripts and required data files
MODELS = {
    'chemprop_logs': {
        'script': 'train_chemprop_logs.py',
        'data_file': 'logs_training_data.csv',
        'description': 'ChemProp LogS (Water Solubility) prediction model',
        'output_dir': '../ChemAPI/chemprop/model/'
    },
    'chemprop_logd': {
        'script': 'train_chemprop_logd.py',
        'data_file': 'logd_training_data.csv',
        'description': 'ChemProp LogD (Distribution Coefficient) prediction model',
        'output_dir': '../ChemAPI/chemprop/model/'
    },
    'metlin': {
        'script': 'train_metlin.py',
        'data_file': 'metlin_training_data.csv',
        'description': 'METLIN Retention Time prediction model',
        'output_dir': '../ChemAPI/metlin/core/'
    }
}


def check_data_file(data_dir, data_file):
    """Check if a training data file exists"""
    data_path = os.path.join(data_dir, data_file)
    return os.path.exists(data_path), data_path


def run_training_script(script_name, data_path, output_dir, dry_run=False):
    """Run a training script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    
    if not os.path.exists(script_path):
        print(f"  ERROR: Training script not found: {script_path}")
        return False
    
    cmd = [
        sys.executable,
        script_path,
        '--data', data_path,
        '--output', output_dir
    ]
    
    if dry_run:
        print(f"  Would run: {' '.join(cmd)}")
        return True
    
    try:
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: Training failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Retrain all ChemAPI models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Retrain all models
  python retrain_all_models.py --all --data-dir ./training_data/
  
  # Retrain only ChemProp models
  python retrain_all_models.py --models chemprop_logs chemprop_logd --data-dir ./training_data/
  
  # Dry run
  python retrain_all_models.py --all --data-dir ./training_data/ --dry-run

Available models:
  chemprop_logs  - LogS (Water Solubility) prediction
  chemprop_logd  - LogD (Distribution Coefficient) prediction
  metlin         - Retention Time prediction
        """
    )
    
    parser.add_argument('--all', action='store_true',
                        help='Retrain all models')
    parser.add_argument('--models', nargs='+', choices=list(MODELS.keys()),
                        help='Specific models to retrain')
    parser.add_argument('--data-dir', required=True,
                        help='Directory containing training data files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without actually training')
    parser.add_argument('--skip-missing', action='store_true',
                        help='Skip models with missing data files instead of failing')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.models:
        parser.error("Must specify either --all or --models")
    
    if not os.path.isdir(args.data_dir):
        parser.error(f"Data directory does not exist: {args.data_dir}")
    
    # Determine which models to train
    if args.all:
        models_to_train = list(MODELS.keys())
    else:
        models_to_train = args.models
    
    print("="*70)
    print("ChemAPI Model Retraining")
    print("="*70)
    print(f"Data directory: {args.data_dir}")
    print(f"Models to train: {', '.join(models_to_train)}")
    if args.dry_run:
        print("DRY RUN MODE - No actual training will be performed")
    print("="*70)
    print()
    
    # Check data files
    print("Checking for training data files...")
    missing_data = []
    for model_name in models_to_train:
        model_info = MODELS[model_name]
        exists, data_path = check_data_file(args.data_dir, model_info['data_file'])
        
        if exists:
            print(f"  ✓ {model_name}: {data_path}")
        else:
            print(f"  ✗ {model_name}: {model_info['data_file']} NOT FOUND")
            missing_data.append(model_name)
    
    print()
    
    if missing_data:
        if args.skip_missing:
            print(f"Skipping models with missing data: {', '.join(missing_data)}")
            models_to_train = [m for m in models_to_train if m not in missing_data]
            if not models_to_train:
                print("No models to train. Exiting.")
                return 0
        else:
            print("ERROR: Missing training data files.")
            print("Use --skip-missing to skip models with missing data.")
            return 1
    
    # Train models
    print("="*70)
    print("Training Models")
    print("="*70)
    print()
    
    results = {}
    for model_name in models_to_train:
        model_info = MODELS[model_name]
        print(f"Model: {model_name}")
        print(f"Description: {model_info['description']}")
        
        _, data_path = check_data_file(args.data_dir, model_info['data_file'])
        
        success = run_training_script(
            model_info['script'],
            data_path,
            model_info['output_dir'],
            dry_run=args.dry_run
        )
        
        results[model_name] = success
        print()
    
    # Print summary
    print("="*70)
    print("Training Summary")
    print("="*70)
    
    successful = [m for m, s in results.items() if s]
    failed = [m for m, s in results.items() if not s]
    
    if successful:
        print(f"\n✓ Successfully trained ({len(successful)}):")
        for model in successful:
            print(f"  - {model}")
    
    if failed:
        print(f"\n✗ Failed to train ({len(failed)}):")
        for model in failed:
            print(f"  - {model}")
    
    print()
    print(f"Total: {len(successful)}/{len(results)} models trained successfully")
    
    if not args.dry_run and successful:
        print("\nNext steps:")
        print("1. Restart the Django server to use the new models")
        print("2. Test the API endpoints with test_api.py")
        print("3. Update any model loading code if necessary")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
