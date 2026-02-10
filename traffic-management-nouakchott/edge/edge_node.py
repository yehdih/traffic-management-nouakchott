# edge/edge_node.py
import pandas as pd
import json
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge.traffic_classifier import TrafficClassifier
import config

class EdgeNode:
    """
    Complete Edge Node implementation
    
    Responsibilities:
    1. Collect local traffic data
    2. Train local model
    3. Make real-time predictions
    4. Send model weights to Fog layer via Kafka
    """
    
    def __init__(self, intersection_id, intersection_name, kafka_enabled=False):
        self.intersection_id = intersection_id
        self.intersection_name = intersection_name
        self.classifier = TrafficClassifier(intersection_id)
        self.kafka_enabled = kafka_enabled
        self.producer = None
        
        if kafka_enabled:
            self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka producer"""
        try:
            from kafka import KafkaProducer
            from kafka.errors import KafkaError
        except ImportError:
            print("  ℹ kafka-python not installed. Running in offline mode (no Kafka)")
            self.kafka_enabled = False
            return

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"  ✓ Kafka producer initialized for Edge Node {self.intersection_id}")
        except KafkaError as e:
            print(f"  ✗ Kafka connection failed: {e}")
            print("  Running in offline mode (no Kafka)")
            self.kafka_enabled = False
    
    def train_local_model(self, df):
        """
        Train model on local data only
        """
        print(f"\n{'='*70}")
        print(f"Edge Node {self.intersection_id}: {self.intersection_name}")
        print(f"{'='*70}")
        
        accuracy = self.classifier.train(df)
        
        if accuracy:
            # Save model locally
            model_path = f"data/models/edge_model_intersection_{self.intersection_id}.pkl"
            self.classifier.save_model(model_path)
        
        return accuracy
    
    def predict_traffic_state(self, current_data):
        """
        Predict traffic state for current conditions
        
        Args:
            current_data: dict with traffic features
        """
        if not self.classifier.is_trained:
            return None, None
        
        state, confidence = self.classifier.predict(current_data)
        
        return state, confidence
    
    def send_weights_to_fog(self):
        """
        Send model weights to Fog layer via Kafka
        This is the key part of Federated Learning!
        """
        if not self.classifier.is_trained:
            print("  Model not trained - nothing to send")
            return False
        
        weights = self.classifier.get_model_weights()
        
        if self.kafka_enabled and self.producer:
            try:
                # Send to Kafka topic
                future = self.producer.send(
                    config.KAFKA_TOPIC_EDGE_TO_FOG,
                    weights
                )
                
                # Wait for confirmation
                record_metadata = future.get(timeout=10)
                
                print(f"  ✓ Weights sent to Fog via Kafka")
                print(f"    Topic: {record_metadata.topic}")
                print(f"    Partition: {record_metadata.partition}")
                print(f"    Offset: {record_metadata.offset}")
                
                return True
                
            except Exception as e:
                print(f"  ✗ Failed to send weights: {e}")
                return False
        else:
            # Offline mode - just print weights
            print(f"  ℹ Kafka disabled - weights would be sent:")
            print(json.dumps(weights, indent=2))
            return True
    
    def run_training_cycle(self, df):
        """
        Complete training cycle:
        1. Train local model
        2. Send weights to Fog
        """
        print(f"\n{'='*70}")
        print(f"EDGE NODE {self.intersection_id} - TRAINING CYCLE")
        print(f"{'='*70}")
        
        # Train
        accuracy = self.train_local_model(df)
        
        if accuracy:
            # Send weights
            print(f"\nSending model weights to Fog layer...")
            self.send_weights_to_fog()
        
        return accuracy
    
    def close(self):
        """Cleanup"""
        if self.producer:
            self.producer.close()
            print(f"  ✓ Kafka producer closed")


class MultiEdgeSimulation:
    """
    Simulate multiple Edge nodes working together
    """
    
    def __init__(self, kafka_enabled=False):
        self.nodes = []
        self.kafka_enabled = kafka_enabled
        
        # Create Edge node for each intersection
        for intersection in config.INTERSECTIONS:
            node = EdgeNode(
                intersection_id=intersection['id'],
                intersection_name=intersection['name'],
                kafka_enabled=kafka_enabled
            )
            self.nodes.append(node)
    
    def train_all_nodes(self, df):
        """
        Train all Edge nodes in parallel (simulated)
        """
        print("\n" + "="*70)
        print("TRAINING ALL EDGE NODES")
        print("="*70)
        
        accuracies = {}
        
        for node in self.nodes:
            acc = node.run_training_cycle(df)
            accuracies[node.intersection_id] = acc
        
        # Summary
        print("\n" + "="*70)
        print("TRAINING SUMMARY:")
        print("="*70)
        
        for node_id, acc in accuracies.items():
            if acc:
                print(f"  Intersection {node_id}: {acc:.2%} accuracy")
            else:
                print(f"  Intersection {node_id}: FAILED")
        
        avg_acc = sum([a for a in accuracies.values() if a]) / len([a for a in accuracies.values() if a])
        print(f"\n  Average accuracy across all nodes: {avg_acc:.2%}")
    
    def close_all(self):
        """Close all nodes"""
        for node in self.nodes:
            node.close()


def main():
    """
    Test Edge nodes
    """
    print("="*70)
    print("EDGE COMPUTING LAYER - MULTI-NODE SIMULATION")
    print("="*70)
    
    # Load data
    import os
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("ERROR: No simulation data found!")
        print("Run: python simulation/traffic_simulator.py")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    
    print(f"\nLoading data: {latest_file}\n")
    df = pd.read_csv(filepath)
    
    # Create multi-edge simulation
    # Set kafka_enabled=True if Kafka is running
    multi_edge = MultiEdgeSimulation(kafka_enabled=False)
    
    # Train all nodes
    multi_edge.train_all_nodes(df)
    
    # Cleanup
    multi_edge.close_all()
    
    print("\n" + "="*70)
    print("EDGE LAYER SIMULATION COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()