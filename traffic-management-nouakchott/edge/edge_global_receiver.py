# edge/edge_global_receiver.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
import json
import config

class EdgeGlobalReceiver:
    """
    Edge nodes receive global model from Cloud
    """
    
    def __init__(self):
        self.consumer = None
        self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_CLOUD_TO_EDGE,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='edge-receivers',
                auto_offset_reset='earliest'
            )
            print("✓ Edge Global Receiver initialized (Cloud → Edge)")
            return True
            
        except Exception as e:
            print(f"✗ Kafka setup failed: {e}")
            return False
    
    def receive_global_model(self):
        """
        Receive and apply global model updates
        """
        print("\n" + "="*70)
        print("EDGE NODES - RECEIVING GLOBAL MODEL")
        print("="*70)
        print("Waiting for global model from Cloud...")
        print("(Press Ctrl+C to stop)\n")
        
        try:
            for message in self.consumer:
                data = message.value
                
                print(f"\n✓ Received Global Model Update!")
                print(f"  Round: {data['global_model']['round']}")
                print(f"  Global accuracy: {data['global_model']['global_accuracy']:.2%}")
                print(f"  Feature importances: {data['global_model']['global_feature_importances']}")
                print(f"  Total Edge nodes: {data['global_model']['num_edge_nodes_total']}")
                print(f"\n  → Edge nodes would now update their local models")
                print()
        
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        finally:
            self.close()
    
    def close(self):
        """Cleanup"""
        if self.consumer:
            self.consumer.close()
            print("\n✓ Edge Receiver closed")


def main():
    """
    Run Edge global model receiver
    """
    receiver = EdgeGlobalReceiver()
    receiver.receive_global_model()


if __name__ == "__main__":
    main()