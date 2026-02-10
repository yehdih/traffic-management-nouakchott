# kafka_config/kafka_monitor.py
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from datetime import datetime

class KafkaMonitor:
    """
    Monitor all Kafka topics for debugging
    """
    
    def __init__(self):
        self.consumer = None
    
    def monitor_topic(self, topic_name):
        """
        Monitor a specific topic and display all messages
        """
        try:
            consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                consumer_timeout_ms=5000  # Stop after 5 seconds of no messages
            )
            
            print(f"\n{'='*70}")
            print(f"MONITORING TOPIC: {topic_name}")
            print(f"{'='*70}\n")
            
            message_count = 0
            
            for message in consumer:
                message_count += 1
                data = message.value
                
                print(f"Message #{message_count}")
                print(f"  Partition: {message.partition}")
                print(f"  Offset: {message.offset}")
                print(f"  Data: {json.dumps(data, indent=2)}")
                print()
            
            if message_count == 0:
                print("No messages found in topic (or timeout reached)")
            else:
                print(f"Total messages: {message_count}")
            
            consumer.close()
            
        except Exception as e:
            print(f"✗ Error monitoring topic: {e}")
    
    def monitor_all_topics(self):
        """
        Monitor all project topics
        """
        topics = [
            config.KAFKA_TOPIC_EDGE_TO_FOG,
            config.KAFKA_TOPIC_FOG_TO_CLOUD,
            config.KAFKA_TOPIC_CLOUD_TO_EDGE
        ]
        
        for topic in topics:
            self.monitor_topic(topic)


def main():
    """
    Monitor all Kafka activity
    """
    print("="*70)
    print("KAFKA MONITORING TOOL")
    print("="*70)
    
    monitor = KafkaMonitor()
    monitor.monitor_all_topics()
    
    print("\n" + "="*70)
    print("MONITORING COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()