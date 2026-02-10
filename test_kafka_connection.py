from kafka import KafkaProducer, KafkaConsumer
import json
import time

print("Testing Kafka connection...")

# Test Producer
try:
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✓ Producer connected to Kafka")
    
    # Send test message
    test_message = {"test": "Hello Kafka!", "timestamp": time.time()}
    producer.send('sensor-data-node-1', test_message)
    producer.flush()
    print("✓ Test message sent to topic: sensor-data-node-1")
    
    producer.close()
    
except Exception as e:
    print(f"✗ Producer error: {e}")

# Test Consumer
try:
    consumer = KafkaConsumer(
        'sensor-data-node-1',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        consumer_timeout_ms=5000,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print("✓ Consumer connected to Kafka")
    
    # Read messages
    messages_received = 0
    for message in consumer:
        print(f"✓ Received message: {message.value}")
        messages_received += 1
        break  # Just read one message
    
    if messages_received > 0:
        print("✓ Kafka is working correctly!")
    
    consumer.close()
    
except Exception as e:
    print(f"✗ Consumer error: {e}")

print("\nKafka connection test complete!")