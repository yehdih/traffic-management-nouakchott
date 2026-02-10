# fog/fog_kafka_aggregator.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
import config
from fog_aggregator import MultiFogManager
import time

class FogKafkaAggregator:
    """
    Fog layer with Kafka integration
    
    Workflow:
    1. Consume weights from Edge nodes (edge-to-fog topic)
    2. Aggregate weights regionally
    3. Send aggregated weights to Cloud (fog-to-cloud topic)
    """
    
    def __init__(self):
        self.fog_manager = MultiFogManager()
        self.consumer = None
        self.producer = None
        self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            # Consumer: receive from Edge
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_EDGE_TO_FOG,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='fog-aggregator-group',
                auto_offset_reset='latest'  # Only new messages
            )
            print("✓ Kafka Consumer initialized (Edge → Fog)")
            
            # Producer: send to Cloud
            self.producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✓ Kafka Producer initialized (Fog → Cloud)")
            
            return True
            
        except KafkaError as e:
            print(f"✗ Kafka setup failed: {e}")
            return False
    
    def process_edge_weights(self, message):
        """
        Process incoming weights from Edge
        """
        data = message.value
        
        print(f"\n✓ Received from Edge {data['intersection_id']}")
        
        # Route to appropriate Fog node (pass the full message so it includes intersection_id)
        fog_id = self.fog_manager.route_edge_weights(data)
        
        # Check if this Fog region is ready to aggregate
        if fog_id:
            fog_node = self.fog_manager.fog_nodes[fog_id]
            
            if fog_node.is_ready_to_aggregate():
                print(f"\n  → {fog_id} ready to aggregate!")
                self.aggregate_and_send_to_cloud(fog_id)
    
    def aggregate_and_send_to_cloud(self, fog_id):
        """
        Aggregate weights for a Fog region and send to Cloud
        """
        fog_node = self.fog_manager.fog_nodes[fog_id]
        
        # Aggregate
        aggregated = fog_node.aggregate_weights_fedavg()
        
        if aggregated and self.producer:
            # Send to Cloud via Kafka
            message = {
                'fog_id': fog_id,
                'aggregated_weights': aggregated,
                'message_type': 'fog_aggregated'
            }
            
            try:
                future = self.producer.send(
                    config.KAFKA_TOPIC_FOG_TO_CLOUD,
                    value=message
                )
                
                record_metadata = future.get(timeout=10)
                
                print(f"\n  ✓ Aggregated weights sent to Cloud")
                print(f"    Topic: {record_metadata.topic}")
                print(f"    Partition: {record_metadata.partition}")
                
                # Reset for next round
                fog_node.reset()
                
                return True
                
            except Exception as e:
                print(f"  ✗ Failed to send to Cloud: {e}")
                return False
    
    def start_consuming(self, timeout_seconds=None):
        """
        Start consuming Edge weights and aggregating
        
        Args:
            timeout_seconds: Run for X seconds (None = infinite)
        """
        print("\n" + "="*70)
        print("FOG LAYER - KAFKA AGGREGATOR STARTED")
        print("="*70)
        print("Waiting for Edge weights...")
        print("(Press Ctrl+C to stop)\n")
        
        start_time = time.time()
        
        try:
            for message in self.consumer:
                self.process_edge_weights(message)
                
                # Check timeout
                if timeout_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout_seconds:
                        print(f"\nTimeout reached ({timeout_seconds}s)")
                        break
        
        except KeyboardInterrupt:
            print("\nStopped by user")
        
        finally:
            self.close()
    
    def close(self):
        """Cleanup"""
        if self.consumer:
            self.consumer.close()
            print("\n✓ Consumer closed")
        
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("✓ Producer closed")


def main():
    """
    Run the Fog Kafka aggregator
    """
    aggregator = FogKafkaAggregator()
    
    # Start consuming (run indefinitely until Ctrl+C)
    aggregator.start_consuming()
    
    print("\n" + "="*70)
    print("FOG AGGREGATOR STOPPED")
    print("="*70)


if __name__ == "__main__":
    main()