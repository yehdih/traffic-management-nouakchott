# cloud/cloud_consumer.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
import json
import config

class CloudConsumer:
    """
    Cloud layer receives aggregated weights from Fog
    """
    
    def __init__(self):
        self.consumer = None
        self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_FOG_TO_CLOUD,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='cloud-receiver',
                auto_offset_reset='earliest'
            )
            print("✓ Cloud Consumer initialized (Fog → Cloud)")
            return True
            
        except Exception as e:
            print(f"✗ Kafka setup failed: {e}")
            return False
    
    def consume_fog_weights(self):
        """
        Consume aggregated weights from Fog
        """
        print("\n" + "="*70)
        print("CLOUD LAYER - RECEIVING FOG AGGREGATIONS")
        print("="*70)
        print("Waiting for Fog aggregations...")
        print("(Press Ctrl+C to stop)\n")
        
        try:
            for message in self.consumer:
                data = message.value
                
                print(f"\n✓ Received from {data['fog_id']}")
                print(f"  Region: {data['aggregated_weights']['region_name']}")
                print(f"  Edge nodes: {data['aggregated_weights']['num_edge_nodes']}")
                print(f"  Avg accuracy: {data['aggregated_weights']['average_accuracy']:.2%}")
                print(f"  Feature importances: {data['aggregated_weights']['aggregated_feature_importances']}")
                print()
        
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        finally:
            self.close()
    
    def close(self):
        """Cleanup"""
        if self.consumer:
            self.consumer.close()
            print("\n✓ Cloud Consumer closed")


def main():
    """
    Run Cloud consumer
    """
    consumer = CloudConsumer()
    consumer.consume_fog_weights()


if __name__ == "__main__":
    main()