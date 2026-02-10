# kafka_config/create_topics.py
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def create_kafka_topics():
    """
    Create Kafka topics for our architecture:
    - edge-to-fog: Edge nodes send weights to Fog
    - fog-to-cloud: Fog sends aggregated weights to Cloud
    - cloud-to-edge: Cloud sends global model back to Edge
    """
    
    print("="*70)
    print("CREATING KAFKA TOPICS")
    print("="*70)
    
    try:
        # Connect to Kafka
        admin_client = KafkaAdminClient(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            client_id='topic_creator'
        )
        
        # Define topics
        topics = [
            NewTopic(
                name=config.KAFKA_TOPIC_EDGE_TO_FOG,
                num_partitions=3,  # Allow parallel processing
                replication_factor=1
            ),
            NewTopic(
                name=config.KAFKA_TOPIC_FOG_TO_CLOUD,
                num_partitions=1,
                replication_factor=1
            ),
            NewTopic(
                name=config.KAFKA_TOPIC_CLOUD_TO_EDGE,
                num_partitions=1,
                replication_factor=1
            )
        ]
        
        # Create topics
        admin_client.create_topics(new_topics=topics, validate_only=False)
        
        print("\n✓ Topics created successfully:")
        for topic in topics:
            print(f"  - {topic.name} (partitions: {topic.num_partitions})")
        
        admin_client.close()
        
    except TopicAlreadyExistsError:
        print("\nℹ Topics already exist (this is OK)")
    
    except Exception as e:
        print(f"\n✗ Error creating topics: {e}")
        print("\nMake sure Kafka is running:")
        print("  docker-compose up -d")


def list_kafka_topics():
    """
    List all existing Kafka topics
    """
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            client_id='topic_lister'
        )
        
        topics = admin_client.list_topics()
        
        print("\n" + "="*70)
        print("EXISTING KAFKA TOPICS:")
        print("="*70)
        for topic in topics:
            print(f"  - {topic}")
        
        admin_client.close()
        
    except Exception as e:
        print(f"✗ Error listing topics: {e}")


def main():
    create_kafka_topics()
    list_kafka_topics()


if __name__ == "__main__":
    main()