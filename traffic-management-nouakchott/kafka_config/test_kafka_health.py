# kafka_config/test_kafka_health.py
from kafka import KafkaAdminClient, KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import json

def test_kafka_connection():
    """Test basic Kafka connectivity"""
    print("\n1. Testing Kafka Connection...")
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            client_id='health_check'
        )
        admin.close()
        print("   ✓ Kafka is reachable")
        return True
    except Exception as e:
        print(f"   ✗ Cannot connect to Kafka: {e}")
        return False

def test_topics_exist():
    """Test if required topics exist"""
    print("\n2. Testing Topics...")
    try:
        admin = KafkaAdminClient(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS
        )
        existing_topics = admin.list_topics()
        
        required_topics = [
            config.KAFKA_TOPIC_EDGE_TO_FOG,
            config.KAFKA_TOPIC_FOG_TO_CLOUD,
            config.KAFKA_TOPIC_CLOUD_TO_EDGE
        ]
        
        for topic in required_topics:
            if topic in existing_topics:
                print(f"   ✓ Topic exists: {topic}")
            else:
                print(f"   ✗ Topic missing: {topic}")
        
        admin.close()
        return True
        
    except Exception as e:
        print(f"   ✗ Error checking topics: {e}")
        return False

def test_producer():
    """Test producer"""
    print("\n3. Testing Producer...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Send test message
        producer.send('test-topic', {'test': 'health_check'})
        producer.flush()
        producer.close()
        
        print("   ✓ Producer works")
        return True
        
    except Exception as e:
        print(f"   ✗ Producer failed: {e}")
        return False

def test_consumer():
    """Test consumer"""
    print("\n4. Testing Consumer...")
    try:
        consumer = KafkaConsumer(
            config.KAFKA_TOPIC_EDGE_TO_FOG,
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            consumer_timeout_ms=1000
        )
        consumer.close()
        
        print("   ✓ Consumer works")
        return True
        
    except Exception as e:
        print(f"   ✗ Consumer failed: {e}")
        return False

def main():
    """
    Complete Kafka health check
    """
    print("="*70)
    print("KAFKA HEALTH CHECK")
    print("="*70)
    
    results = []
    
    results.append(test_kafka_connection())
    results.append(test_topics_exist())
    results.append(test_producer())
    results.append(test_consumer())
    
    print("\n" + "="*70)
    print("HEALTH CHECK SUMMARY")
    print("="*70)
    
    if all(results):
        print("\n✓ ALL TESTS PASSED - Kafka is healthy!")
    else:
        print("\n✗ SOME TESTS FAILED - Check errors above")
        print("\nTroubleshooting:")
        print("  1. Make sure Docker is running")
        print("  2. Run: docker-compose up -d")
        print("  3. Run: python kafka_config/create_topics.py")
    
    print()

if __name__ == "__main__":
    main()