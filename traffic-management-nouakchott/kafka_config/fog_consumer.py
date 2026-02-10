# kafka_config/fog_consumer.py
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class FogKafkaConsumer:
    """
    Kafka consumer for Fog layer
    Receives model weights from Edge nodes
    """
    
    def __init__(self, group_id='fog-aggregator'):
        self.consumer = None
        self.group_id = group_id
        self.connect()
    
    def connect(self):
        """Connect to Kafka broker and subscribe to topic"""
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_EDGE_TO_FOG,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',  # Start from beginning if no offset
                enable_auto_commit=True
            )
            print(f"✓ Fog Kafka Consumer connected")
            print(f"  Topic: {config.KAFKA_TOPIC_EDGE_TO_FOG}")
            print(f"  Group ID: {self.group_id}")
            return True
            
        except KafkaError as e:
            print(f"✗ Failed to connect to Kafka: {e}")
            return False
    
    def consume_weights(self, timeout_ms=10000, max_messages=None):
        """
        Consume model weights from Edge nodes
        
        Args:
            timeout_ms: How long to wait for messages
            max_messages: Maximum number of messages to consume (None = infinite)
        
        Returns:
            List of received weights
        """
        if not self.consumer:
            print("✗ Consumer not connected")
            return []
        
        received_weights = []
        message_count = 0
        
        print("\nListening for messages...")
        print("(Press Ctrl+C to stop)\n")
        
        try:
            for message in self.consumer:
                data = message.value
                
                print(f"✓ Received from Edge {data['intersection_id']}")
                print(f"  Timestamp: {data['timestamp']}")
                print(f"  Weights: {data['weights']}")
                print()
                
                received_weights.append(data)
                message_count += 1
                
                # Stop if we've received enough messages
                if max_messages and message_count >= max_messages:
                    break
        
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        return received_weights
    
    def close(self):
        """Close consumer connection"""
        if self.consumer:
            self.consumer.close()
            print("✓ Fog Consumer closed")


def test_consumer():
    """
    Test the Fog consumer
    """
    print("="*70)
    print("TESTING FOG KAFKA CONSUMER")
    print("="*70)
    print("\nMake sure you've run edge_producer.py first!")
    print("Or run it in another terminal while this is running.\n")
    
    consumer = FogKafkaConsumer()
    
    # Consume up to 5 messages (or Ctrl+C to stop)
    weights = consumer.consume_weights(max_messages=5)
    
    print("\n" + "="*70)
    print(f"RECEIVED {len(weights)} MESSAGES")
    print("="*70)
    
    consumer.close()


if __name__ == "__main__":
    test_consumer()