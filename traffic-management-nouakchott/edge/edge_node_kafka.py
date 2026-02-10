# edge/edge_node_kafka.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from edge.edge_node import EdgeNode
from kafka_config.edge_producer import EdgeKafkaProducer
import config
import time

class EdgeNodeWithKafka:
    """
    Edge Node with Kafka integration
    """
    
    def __init__(self, intersection_id, intersection_name):
        self.edge_node = EdgeNode(
            intersection_id=intersection_id,
            intersection_name=intersection_name,
            kafka_enabled=False  # We'll use our own producer
        )
        self.kafka_producer = EdgeKafkaProducer()
    
    def train_and_send(self, df):
        """
        Complete workflow:
        1. Train local model
        2. Extract weights
        3. Send to Fog via Kafka
        """
        print(f"\n{'='*70}")
        print(f"EDGE NODE {self.edge_node.intersection_id} - KAFKA WORKFLOW")
        print(f"{'='*70}")
        
        # Train
        accuracy = self.edge_node.train_local_model(df)
        
        if accuracy:
            # Get weights
            weights = self.edge_node.classifier.get_model_weights()
            
            # Add accuracy to weights if not already there
            if 'accuracy' not in weights:
                weights['accuracy'] = accuracy
            
            # Send via Kafka
            print("\nSending weights to Fog via Kafka...")
            success = self.kafka_producer.send_model_weights(
                self.edge_node.intersection_id,
                weights
            )
            
            if success:
                print("✓ Weights successfully sent to Fog layer")
            else:
                print("✗ Failed to send weights")
        
        return accuracy
    
    def close(self):
        """Cleanup"""
        self.kafka_producer.close()


def run_multi_edge_kafka_demo():
    """
    Demonstrate multiple Edge nodes sending to Kafka
    """
    print("="*70)
    print("MULTI-EDGE KAFKA DEMONSTRATION")
    print("="*70)
    
    # Load data
    import os
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("ERROR: No simulation data found!")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    
    print(f"\nLoading data: {latest_file}\n")
    df = pd.read_csv(filepath)
    
    # Create Edge nodes for first 3 intersections
    edge_nodes = []
    for i in range(1, 4):  # Intersections 1, 2, 3
        intersection = config.INTERSECTIONS[i-1]
        node = EdgeNodeWithKafka(
            intersection_id=intersection['id'],
            intersection_name=intersection['name']
        )
        edge_nodes.append(node)
    
    # Train and send weights
    for node in edge_nodes:
        node.train_and_send(df)
        time.sleep(2)  # Small delay between nodes
    
    # Cleanup
    for node in edge_nodes:
        node.close()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print("\nNow run the Fog consumer to see the messages:")
    print("  python kafka_config/fog_consumer.py")


if __name__ == "__main__":
    run_multi_edge_kafka_demo()