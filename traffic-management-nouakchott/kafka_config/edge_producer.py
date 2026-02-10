# kafka_config/edge_producer.py
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class EdgeKafkaProducer:
    """
    Kafka producer for Edge nodes
    Sends model weights to Fog layer
    """
    
    def __init__(self):
        self.producer = None
        self.connect()
    
    def connect(self):
        """Connect to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3
            )
            print("✓ Edge Kafka Producer connected")
            return True
            
        except KafkaError as e:
            print(f"✗ Failed to connect to Kafka: {e}")
            return False
    
    def send_model_weights(self, intersection_id, weights):
        """
        Send model weights from Edge to Fog
        
        Args:
            intersection_id: Which intersection
            weights: Model parameters (dict)
        """
        if not self.producer:
            print("✗ Producer not connected")
            return False
        
        # Add metadata
        message = {
            'intersection_id': intersection_id,
            'timestamp': datetime.now().isoformat(),
            'weights': weights,
            'message_type': 'edge_weights'
        }
        
        try:
            # Send asynchronously
            future = self.producer.send(
                config.KAFKA_TOPIC_EDGE_TO_FOG,
                value=message
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            print(f"✓ Weights sent from Edge {intersection_id}")
            print(f"  Topic: {record_metadata.topic}")
            print(f"  Partition: {record_metadata.partition}")
            print(f"  Offset: {record_metadata.offset}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to send weights: {e}")
            return False
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.flush()  # Make sure all messages are sent
            self.producer.close()
            print("✓ Edge Producer closed")


def test_producer():
    """
    Test the Edge producer
    """
    print("="*70)
    print("TESTING EDGE KAFKA PRODUCER")
    print("="*70)
    
    producer = EdgeKafkaProducer()
    
    # Simulate sending weights from 3 intersections
    for i in range(1, 4):
        weights = {
            'n_estimators': 50,
            'feature_importances': [0.3, 0.4, 0.2, 0.1],
            'accuracy': 0.85 + (i * 0.02)
        }
        
        print(f"\nSending from Intersection {i}...")
        producer.send_model_weights(i, weights)
        time.sleep(1)
    
    producer.close()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_producer()