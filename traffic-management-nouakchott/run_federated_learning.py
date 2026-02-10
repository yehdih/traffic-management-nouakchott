# run_federated_learning.py
import subprocess
import time
import sys
import os

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70 + "\n")

def check_kafka():
    """Check if Kafka is running"""
    print_header("CHECKING KAFKA STATUS")
    
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True
        )
        
        if 'kafka' in result.stdout:
            print("✓ Kafka is running")
            return True
        else:
            print("✗ Kafka is not running")
            print("\nStart Kafka with: docker-compose up -d")
            return False
            
    except Exception as e:
        print(f"✗ Error checking Kafka: {e}")
        return False

def run_simulation():
    """Run complete federated learning simulation"""
    
    print_header("FEDERATED LEARNING SIMULATION")
    print("This will simulate one complete round of federated learning")
    print("Edge → Fog → Cloud → Edge\n")
    
    input("Press Enter to start...")
    
    # Step 1: Start Cloud server (in background)
    print_header("STEP 1: Starting Cloud Server")
    # Note: In real scenario, you'd start this in a separate terminal
    print("In production, run in Terminal 1: python cloud/cloud_kafka_server.py")
    
    # Step 2: Start Fog aggregator (in background)
    print_header("STEP 2: Starting Fog Aggregator")
    print("In production, run in Terminal 2: python fog/fog_kafka_aggregator.py")
    
    # Step 3: Start Edge global receiver (in background)
    print_header("STEP 3: Starting Edge Global Receiver")
    print("In production, run in Terminal 3: python edge/edge_global_receiver.py")
    
    # Step 4: Run Edge training and send weights
    print_header("STEP 4: Running Edge Training")
    print("In production, run in Terminal 4: python edge/edge_node_kafka.py")
    
    print_header("SIMULATION INSTRUCTIONS")
    print("""
To run the complete simulation, open 4 terminals and run:

Terminal 1 (Cloud):
    python cloud/cloud_kafka_server.py

Terminal 2 (Fog):
    python fog/fog_kafka_aggregator.py

Terminal 3 (Edge Receiver):
    python edge/edge_global_receiver.py

Terminal 4 (Edge Senders):
    python edge/edge_node_kafka.py

Then watch the magic happen! The flow will be:
  Edge (train) → Fog (aggregate) → Cloud (global) → Edge (update)
    """)

def main():
    """
    Main orchestration
    """
    print_header("NOUAKCHOTT TRAFFIC MANAGEMENT - FEDERATED LEARNING")
    
    # Check Kafka
    if not check_kafka():
        print("\nPlease start Kafka first, then run this script again.")
        return
    
    # Run simulation
    run_simulation()

if __name__ == "__main__":
    main()