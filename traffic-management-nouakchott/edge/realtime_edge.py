# edge/realtime_edge.py
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.realtime_simulator import RealtimeTrafficSimulator
from edge_node import EdgeNode
import pandas as pd

class RealtimeEdgeProcessor:
    """
    Process traffic data in real-time at the Edge
    """
    
    def __init__(self, intersection_id=1):
        self.intersection_id = intersection_id
        self.edge_node = EdgeNode(
            intersection_id=intersection_id,
            intersection_name=f"Intersection {intersection_id}",
            kafka_enabled=False
        )
        
        # Load pre-trained model if exists
        model_path = f"data/models/edge_model_intersection_{intersection_id}.pkl"
        if os.path.exists(model_path):
            self.edge_node.classifier.load_model(model_path)
            print(f"✓ Loaded pre-trained model for intersection {intersection_id}")
        else:
            print(f"ℹ No pre-trained model found. Train first!")
    
    def process_data_point(self, data):
        """
        Process one data point in real-time
        """
        features = {
            'vehicle_count': data['vehicle_count'],
            'avg_speed_kmh': data['avg_speed_kmh'],
            'density': data['density'],
            'hour': data['hour']
        }
        
        # Predict
        predicted_state, confidence = self.edge_node.predict_traffic_state(features)
        
        # Compare with actual (be defensive: predicted_state or confidence may be None)
        actual_state = data['traffic_state']
        correct = "✓" if predicted_state == actual_state else "✗"

        actual_state_str = str(actual_state) if actual_state is not None else "N/A"
        predicted_state_str = str(predicted_state) if predicted_state is not None else "N/A"
        confidence_str = f"{confidence:.2%}" if (confidence is not None and isinstance(confidence, (int, float))) else "N/A"

        print(f"  {correct} Actual: {actual_state_str:8s} | Predicted: {predicted_state_str:8s} | Confidence: {confidence_str}")
        
        return predicted_state, confidence


def main():
    """
    Real-time Edge processing demo
    """
    print("="*70)
    print("REAL-TIME EDGE PROCESSING")
    print("="*70)
    
    # Check if model exists
    processor = RealtimeEdgeProcessor(intersection_id=1)
    
    if not processor.edge_node.classifier.is_trained:
        print("\nERROR: Model not trained!")
        print("Run first: python edge/edge_node.py")
        return
    
    # Load some test data
    import os
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("ERROR: No simulation data found!")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    df = pd.read_csv(filepath)
    
    # Filter for intersection 1
    test_data = df[df['intersection_id'] == 1].head(20)
    
    print(f"\nProcessing {len(test_data)} real-time data points...")
    print("="*70)
    
    correct_predictions = 0
    
    for idx, row in test_data.iterrows():
        predicted, conf = processor.process_data_point(row)
        
        if predicted == row['traffic_state']:
            correct_predictions += 1
        
        time.sleep(0.5)  # Simulate real-time delay
    
    accuracy = correct_predictions / len(test_data)
    
    print("\n" + "="*70)
    print(f"Real-time Accuracy: {accuracy:.2%} ({correct_predictions}/{len(test_data)})")
    print("="*70)


if __name__ == "__main__":
    main()