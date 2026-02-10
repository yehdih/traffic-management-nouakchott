# test_kafka.py
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import time

def test_kafka_connection():
    """Test if Kafka is running and accessible"""
    try:
        # Try to create a producer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Send a test message
        test_data = {'test': 'Hello Kafka!', 'timestamp': time.time()}
        producer.send('test-topic', test_data)
        producer.flush()
        
        print("✓ Kafka connection successful!")
        print("✓ Test message sent to 'test-topic'")
        
        producer.close()
        return True
        
    except KafkaError as e:
        print(f"✗ Kafka connection failed: {e}")
        print("\nMake sure Kafka is running:")
        print("  docker-compose up -d")
        return False

if __name__ == "__main__":
    print("Testing Kafka connection...")
    test_kafka_connection()