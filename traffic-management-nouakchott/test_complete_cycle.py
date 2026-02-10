# test_complete_cycle.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from edge.edge_node_kafka import EdgeNodeWithKafka
import config
import time

def send_all_edge_weights():
    """
    Send weights from ALL edge nodes to trigger complete cycle
    """
    print("="*70)
    print("SENDING WEIGHTS FROM ALL EDGE NODES")
    print("="*70)
    
    # Load data
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("ERROR: No simulation data found!")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    
    print(f"\nLoading data: {latest_file}\n")
    df = pd.read_csv(filepath)
    
    # Send from ALL 10 intersections
    for intersection in config.INTERSECTIONS:
        print(f"\n{'='*70}")
        print(f"Processing Intersection {intersection['id']}")
        print(f"{'='*70}")
        
        node = EdgeNodeWithKafka(
            intersection_id=intersection['id'],
            intersection_name=intersection['name']
        )
        
        # Train and send
        node.train_and_send(df)
        node.close()
        
        # Small delay
        time.sleep(1)
    
    print("\n" + "="*70)
    print("ALL EDGE NODES SENT WEIGHTS!")
    print("="*70)
    print("\nCheck other terminals to see:")
    print("  - Fog aggregating regions")
    print("  - Cloud creating global model")
    print("  - Edge receiving global model")

if __name__ == "__main__":
    send_all_edge_weights()