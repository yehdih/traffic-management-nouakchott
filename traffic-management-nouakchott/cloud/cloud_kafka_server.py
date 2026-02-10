# cloud/cloud_kafka_server.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
import config
from cloud_server import CloudFederatedServer
import time

class CloudKafkaServer:
    """
    Cloud server with full Kafka integration
    
    Workflow:
    1. Consume aggregated weights from Fog (fog-to-cloud)
    2. Perform global FedAvg
    3. Send global model back to Edge (cloud-to-edge)
    """
    
    def __init__(self):
        self.cloud_server = CloudFederatedServer()
        self.consumer = None
        self.producer = None
        self.setup_kafka()
    
    def setup_kafka(self):
        """Initialize Kafka consumer and producer"""
        try:
            # Consumer: receive from Fog
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC_FOG_TO_CLOUD,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='cloud-server-group',
                auto_offset_reset='latest'
            )
            print("✓ Kafka Consumer initialized (Fog → Cloud)")
            
            # Producer: send to Edge
            self.producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("✓ Kafka Producer initialized (Cloud → Edge)")
            
            return True
            
        except KafkaError as e:
            print(f"✗ Kafka setup failed: {e}")
            return False
    
    def process_fog_weights(self, message):
        """
        Process incoming aggregated weights from Fog
        """
        data = message.value
        
        # Receive weights
        self.cloud_server.receive_fog_weights(data)
        
        # Check if ready for global aggregation
        if self.cloud_server.is_ready_for_global_aggregation():
            print("\n" + "="*70)
            print("ALL FOG NODES RECEIVED - PERFORMING GLOBAL AGGREGATION")
            print("="*70)
            
            # Perform global FedAvg
            global_model = self.cloud_server.global_fedavg()
            
            if global_model:
                # Send global model back to Edge
                self.send_global_model_to_edge(global_model)
                
                # Reset for next round
                self.cloud_server.reset_for_next_round()
    
    def send_global_model_to_edge(self, global_model):
        """
        Send global model to Edge nodes via Kafka
        """
        if not self.producer:
            print("✗ Producer not initialized")
            return False
        
        distribution = self.cloud_server.prepare_model_for_distribution()
        
        try:
            future = self.producer.send(
                config.KAFKA_TOPIC_CLOUD_TO_EDGE,
                value=distribution
            )
            
            record_metadata = future.get(timeout=10)
            
            print(f"\n✓ Global model sent to Edge nodes")
            print(f"  Topic: {record_metadata.topic}")
            print(f"  Partition: {record_metadata.partition}")
            print(f"  Offset: {record_metadata.offset}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to send global model: {e}")
            return False
    
    def start_server(self, timeout_seconds=None):
        """
        Start the Cloud server
        
        Args:
            timeout_seconds: Run for X seconds (None = infinite)
        """
        print("\n" + "="*70)
        print("CLOUD FEDERATED LEARNING SERVER STARTED")
        print("="*70)
        print("Waiting for Fog aggregations...")
        print("(Press Ctrl+C to stop)\n")
        
        start_time = time.time()
        
        try:
            for message in self.consumer:
                self.process_fog_weights(message)
                
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
        
        # Print final statistics
        self.cloud_server.print_statistics()


def main():
    """
    Run the Cloud Kafka server
    """
    server = CloudKafkaServer()
    
    # Start server (run indefinitely until Ctrl+C)
    server.start_server()
    
    print("\n" + "="*70)
    print("CLOUD SERVER STOPPED")
    print("="*70)


if __name__ == "__main__":
    main()