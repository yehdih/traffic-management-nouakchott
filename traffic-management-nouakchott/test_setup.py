# test_setup.py
import sys
import pandas as pd
import numpy as np
import sklearn
from kafka import KafkaProducer, KafkaConsumer
import streamlit
import config

def test_imports():
    """Test all required imports"""
    print("✓ All packages imported successfully!")
    print(f"  - Pandas: {pd.__version__}")
    print(f"  - NumPy: {np.__version__}")
    print(f"  - Scikit-learn: {sklearn.__version__}")
    print(f"  - Streamlit: {streamlit.__version__}")
    
def test_folders():
    """Test folder structure"""
    import os
    folders = ['data', 'data/simulated', 'data/models', 'edge', 
               'fog', 'cloud', 'simulation', 'visualization']
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"✓ Folder exists: {folder}")
        else:
            print(f"✗ Missing folder: {folder}")
            
def test_config():
    """Test configuration"""
    print(f"✓ Config loaded successfully!")
    print(f"  - Number of intersections: {config.NUM_INTERSECTIONS}")
    print(f"  - Kafka server: {config.KAFKA_BOOTSTRAP_SERVERS}")

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING PROJECT SETUP")
    print("=" * 50)
    
    print("\n1. Testing Imports...")
    test_imports()
    
    print("\n2. Testing Folder Structure...")
    test_folders()
    
    print("\n3. Testing Configuration...")
    test_config()
    
    print("\n" + "=" * 50)
    print("SETUP TEST COMPLETE!")
    print("=" * 50)