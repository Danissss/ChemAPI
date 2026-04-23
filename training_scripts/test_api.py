#!/usr/bin/env python3
"""
Test script for ChemAPI endpoints
Tests both GET (legacy) and POST (recommended) methods
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

# Test cases with simple SMILES (should work with both GET and POST)
SIMPLE_TESTS = [
    {
        "name": "Pyridine",
        "smiles": "C1=CC=CN=C1",
        "description": "Simple aromatic heterocycle"
    },
    {
        "name": "Ethanol",
        "smiles": "CCO",
        "description": "Simple alcohol"
    }
]

# Test cases with complex structures or special chars (POST only)
COMPLEX_TESTS = [
    {
        "name": "Aspirin",
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "description": "Acetylsalicylic acid"
    }
]

# DarkChem specific tests
DARKCHEM_TESTS = [
    {
        "name": "Pyridine protonated",
        "smiles": "C1=CC=CN=C1",
        "adduct": "[M+H]+",
        "description": "Protonated pyridine"
    },
    {
        "name": "Pyridine deprotonated",
        "smiles": "C1=CC=CN=C1",
        "adduct": "[M-H]-",
        "description": "Deprotonated pyridine"
    },
    {
        "name": "Pyridine sodiated",
        "smiles": "C1=CC=CN=C1",
        "adduct": "[M+Na]+",
        "description": "Sodiated pyridine"
    }
]

# DeepCCS specific tests
DEEPCCS_TESTS = [
    {
        "name": "Pyridine M+H",
        "smiles": "C1=CC=CN=C1",
        "adduct": "M+H",
        "description": "Protonated pyridine"
    },
    {
        "name": "Ethanol M+Na",
        "smiles": "CCO",
        "adduct": "M+Na",
        "description": "Sodiated ethanol"
    },
    {
        "name": "Pyridine M-H",
        "smiles": "C1=CC=CN=C1",
        "adduct": "M-H",
        "description": "Deprotonated pyridine"
    }
]
def test_endpoint_post(url, payload, test_name):
    """Test an endpoint using POST method"""
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'error' not in result:
                print(f"✓ {test_name} (POST): SUCCESS")
                return True
            else:
                print(f"✗ {test_name} (POST): ERROR - {result['error']}")
                return False
        else:
            print(f"✗ {test_name} (POST): HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('error', 'Unknown error')}")
            except Exception:
                print(f"  Response: {response.text[:100]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ {test_name} (POST): Cannot connect to server")
        return False
    except Exception as e:
        print(f"✗ {test_name} (POST): {str(e)}")
        return False

def test_endpoint_get(url, test_name):
    """Test an endpoint using GET method (legacy)"""
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' not in result:
                print(f"✓ {test_name} (GET): SUCCESS")
                return True
            else:
                print(f"✗ {test_name} (GET): ERROR - {result['error']}")
                return False
        else:
            print(f"✗ {test_name} (GET): HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ {test_name} (GET): Cannot connect to server")
        return False
    except Exception as e:
        print(f"✗ {test_name} (GET): {str(e)}")
        return False

def main():
    print("=" * 60)
    print("ChemAPI Test Suite")
    print("=" * 60)
    print(f"Testing server at: {BASE_URL}")
    print()
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=5)
    except:
        print("ERROR: Cannot connect to server. Please start the server with:")
        print("  python manage.py runserver")
        sys.exit(1)
    
    total_tests = 0
    passed_tests = 0
    
    # Test ChemProp endpoints
    print("\n" + "=" * 60)
    print("Testing ChemProp Endpoints")
    print("=" * 60)
    
    for test in SIMPLE_TESTS:
        print(f"\nTesting: {test['name']} ({test['description']})")
        
        # Test POST
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/chemprop/predict/",
            {"structure": test["smiles"]},
            "ChemProp All Properties"
        ):
            passed_tests += 1
        
        # Test GET (legacy)
        total_tests += 1
        if test_endpoint_get(
            f"{BASE_URL}/chemprop/predict/{test['smiles']}/",
            "ChemProp All Properties"
        ):
            passed_tests += 1
        
        # Test LogS POST
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/chemprop/predict/logs/",
            {"structure": test["smiles"]},
            "ChemProp LogS"
        ):
            passed_tests += 1
        
        # Test LogD POST
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/chemprop/predict/logd/",
            {"structure": test["smiles"]},
            "ChemProp LogD"
        ):
            passed_tests += 1
    
    # Test METLIN endpoints
    print("\n" + "=" * 60)
    print("Testing METLIN Endpoints")
    print("=" * 60)
    
    for test in SIMPLE_TESTS:
        print(f"\nTesting: {test['name']} ({test['description']})")
        
        # Test POST
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/metlin/predict/",
            {"structure": test["smiles"]},
            "METLIN Retention Time"
        ):
            passed_tests += 1
    
    # Test RapidMiner endpoints
    print("\n" + "=" * 60)
    print("Testing RapidMiner Endpoints")
    print("=" * 60)
    
    for test in SIMPLE_TESTS:
        print(f"\nTesting: {test['name']} ({test['description']})")
        
        # Test POST
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/rapidminer/predict/",
            {"structure": test["smiles"]},
            "RapidMiner Retention Index"
        ):
            passed_tests += 1
    
    # Test DarkChem endpoints
    print("\n" + "=" * 60)
    print("Testing DarkChem Endpoints")
    print("=" * 60)
    
    for test in DARKCHEM_TESTS:
        print(f"\nTesting: {test['name']} ({test['description']})")
        
        # Test POST with adduct
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/darkchem/predict/",
            {"structure": test["smiles"], "adduct": test["adduct"]},
            f"DarkChem {test['adduct']}"
        ):
            passed_tests += 1
    
    # Test DeepCCS endpoints
    print("\n" + "=" * 60)
    print("Testing DeepCCS Endpoints")
    print("=" * 60)
    
    for test in DEEPCCS_TESTS:
        print(f"\nTesting: {test['name']} ({test['description']})")
        
        # Test POST with adduct
        total_tests += 1
        if test_endpoint_post(
            f"{BASE_URL}/deepccs/predict/",
            {"structure": test["smiles"], "adduct": test["adduct"]},
            f"DeepCCS {test['adduct']}"
        ):
            passed_tests += 1
    
    # Test error handling
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    print("\nTesting missing structure:")
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/chemprop/predict/",
            headers={'Content-Type': 'application/json'},
            json={},
            timeout=30
        )
        if response.status_code == 400 and 'error' in response.json():
            print("✓ Missing structure error handling: SUCCESS")
            passed_tests += 1
        else:
            print("✗ Missing structure error handling: FAILED")
    except Exception as e:
        print(f"✗ Missing structure error handling: {str(e)}")
    
    print("\nTesting invalid adduct:")
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/darkchem/predict/",
            headers={'Content-Type': 'application/json'},
            json={"structure": "CCO", "adduct": "INVALID"},
            timeout=30
        )
        if response.status_code == 400 and 'error' in response.json():
            print("✓ Invalid adduct error handling: SUCCESS")
            passed_tests += 1
        else:
            print("✗ Invalid adduct error handling: FAILED")
    except Exception as e:
        print(f"✗ Invalid adduct error handling: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total_tests - passed_tests} test(s) failed")
        print("\nNote: Some failures may be due to missing or incompatible models.")
        print("See MIGRATION_GUIDE.md for information on model compatibility.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
