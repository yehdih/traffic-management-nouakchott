# edge/traffic_classifier.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

class TrafficClassifier:
    """
    Local ML model for traffic state classification
    Uses Random Forest (lightweight, no TensorFlow needed)
    """
    
    def __init__(self, intersection_id):
        self.intersection_id = intersection_id
        self.model = RandomForestClassifier(
            n_estimators=50,      # 50 trees
            max_depth=10,         # Not too deep (prevent overfitting)
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = ['vehicle_count', 'avg_speed_kmh', 'density', 'hour']
        self.label_mapping = {'Fluide': 0, 'Dense': 1, 'Bloqué': 2}
        self.reverse_mapping = {0: 'Fluide', 1: 'Dense', 2: 'Bloqué'}
        
    def prepare_features(self, df):
        """
        Extract features from raw data
        
        Features:
        - vehicle_count: number of vehicles
        - avg_speed_kmh: average speed
        - density: vehicles per lane
        - hour: time of day (traffic patterns vary)
        """
        X = df[self.feature_names].values
        return X
    
    def prepare_labels(self, df):
        """
        Convert traffic state labels to numbers
        Fluide = 0, Dense = 1, Bloqué = 2
        """
        y = df['traffic_state'].map(self.label_mapping).values
        return y
    
    def train(self, df, test_size=0.2):
        """
        Train the model on local data
        
        Args:
            df: DataFrame with traffic data
            test_size: Fraction of data for testing
        """
        print(f"\n[Edge Node {self.intersection_id}] Training model...")
        
        # Filter data for this intersection only
        local_data = df[df['intersection_id'] == self.intersection_id].copy()
        
        if len(local_data) < 10:
            print(f"  WARNING: Only {len(local_data)} samples. Need more data!")
            return None
        
        # Prepare features and labels
        X = self.prepare_features(local_data)
        y = self.prepare_labels(local_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features (important for ML models)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  ✓ Training complete!")
        print(f"  ✓ Training samples: {len(X_train)}")
        print(f"  ✓ Test accuracy: {accuracy:.2%}")
        
        # Detailed report
        print(f"\n  Classification Report:")
        target_names = ['Fluide', 'Dense', 'Bloqué']
        print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
        
        return accuracy
    
    def predict(self, features):
        """
        Predict traffic state for new data
        
        Args:
            features: dict with keys ['vehicle_count', 'avg_speed_kmh', 'density', 'hour']
        
        Returns:
            predicted_state: 'Fluide', 'Dense', or 'Bloqué'
            confidence: probability (0-1)
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Convert to array
        X = np.array([[
            features['vehicle_count'],
            features['avg_speed_kmh'],
            features['density'],
            features['hour']
        ]])
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        predicted_state = self.reverse_mapping[prediction]
        confidence = probabilities[prediction]
        
        return predicted_state, confidence
    
    def get_model_weights(self):
        """
        Extract model parameters to send to Fog/Cloud
        
        In Federated Learning, we send model weights, NOT raw data
        """
        if not self.is_trained:
            return None
        
        # For RandomForest, we extract important parameters
        weights = {
            'intersection_id': self.intersection_id,
            'model_type': 'RandomForest',
            'n_estimators': self.model.n_estimators,
            'feature_importances': self.model.feature_importances_.tolist(),
            'n_samples_trained': self.model.n_estimators * self.model.max_depth,
            'timestamp': datetime.now().isoformat()
        }
        
        return weights
    
    def save_model(self, filepath):
        """Save model to disk"""
        if not self.is_trained:
            print("Model not trained yet!")
            return
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'intersection_id': self.intersection_id,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, filepath)
        print(f"  ✓ Model saved: {filepath}")
    
    def load_model(self, filepath):
        """Load model from disk"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.intersection_id = model_data['intersection_id']
        self.feature_names = model_data['feature_names']
        self.is_trained = True
        
        print(f"  ✓ Model loaded from: {filepath}")


def main():
    """
    Test the Edge classifier
    """
    print("=" * 70)
    print("EDGE COMPUTING - TRAFFIC CLASSIFIER TEST")
    print("=" * 70)
    
    # Load simulated data
    import os
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("ERROR: No simulation data found!")
        print("Run: python simulation/traffic_simulator.py")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    
    print(f"\nLoading data: {latest_file}")
    df = pd.read_csv(filepath)
    
    # Train a model for intersection 1
    print("\n" + "=" * 70)
    classifier = TrafficClassifier(intersection_id=1)
    classifier.train(df)
    
    # Save model
    model_path = "data/models/edge_model_intersection_1.pkl"
    classifier.save_model(model_path)
    
    # Test prediction
    print("\n" + "=" * 70)
    print("TESTING PREDICTIONS:")
    print("=" * 70)
    
    test_cases = [
        {'vehicle_count': 15, 'avg_speed_kmh': 55, 'density': 7.5, 'hour': 10},
        {'vehicle_count': 35, 'avg_speed_kmh': 30, 'density': 17.5, 'hour': 8},
        {'vehicle_count': 60, 'avg_speed_kmh': 10, 'density': 30, 'hour': 18}
    ]
    
    for i, test in enumerate(test_cases, 1):
        state, conf = classifier.predict(test)
        print(f"\nTest {i}:")
        print(f"  Input: {test}")
        print(f"  Prediction: {state} (confidence: {conf:.2%})")
    
    # Extract weights for Federated Learning
    print("\n" + "=" * 70)
    print("MODEL WEIGHTS (for Federated Learning):")
    print("=" * 70)
    weights = classifier.get_model_weights()
    print(json.dumps(weights, indent=2))
    
    print("\n" + "=" * 70)
    print("EDGE CLASSIFIER TEST COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()