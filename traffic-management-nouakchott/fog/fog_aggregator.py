# fog/fog_aggregator.py
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

class FogAggregator:
    """
    Fog node that aggregates model weights from multiple Edge nodes
    Implements FedAvg (Federated Averaging) algorithm
    """
    
    def __init__(self, fog_id, region_name, edge_intersections):
        self.fog_id = fog_id
        self.region_name = region_name
        self.edge_intersections = edge_intersections  # List of intersection IDs
        self.received_weights = []  # Store weights from Edge nodes
        self.aggregated_weights = None
        
        print(f"\n{'='*70}")
        print(f"FOG NODE INITIALIZED: {fog_id}")
        print(f"{'='*70}")
        print(f"  Region: {region_name}")
        print(f"  Monitoring intersections: {edge_intersections}")
    
    def receive_edge_weights(self, edge_weights):
        """
        Receive weights from an Edge node
        
        Args:
            edge_weights: dict containing model weights from Edge
        """
        intersection_id = edge_weights.get('intersection_id')
        
        if intersection_id not in self.edge_intersections:
            print(f"  ⚠ Warning: Intersection {intersection_id} not in this region")
            return False
        
        self.received_weights.append(edge_weights)
        
        print(f"  ✓ Received weights from Edge {intersection_id}")
        print(f"    Progress: {len(self.received_weights)}/{len(self.edge_intersections)} nodes")
        
        return True
    
    def aggregate_weights_fedavg(self):
        """
        Aggregate weights using FedAvg algorithm
        
        FedAvg formula:
        w_global = Σ(n_k / N) * w_k
        
        where:
        - w_k = weights from edge node k
        - n_k = number of samples at node k
        - N = total samples across all nodes
        """
        
        if not self.received_weights:
            print("  ✗ No weights received yet!")
            return None
        
        print(f"\n  Aggregating {len(self.received_weights)} models using FedAvg...")
        
        # Extract feature importances (our main "weights" from RandomForest)
        all_importances = []
        all_accuracies = []
        
        for weights in self.received_weights:
            # Check if weights dictionary exists and has the required keys
            if 'weights' in weights and isinstance(weights['weights'], dict):
                if 'feature_importances' in weights['weights']:
                    importances = weights['weights']['feature_importances']
                    all_importances.append(importances)
                    
                    # Track accuracy if available
                    if 'accuracy' in weights['weights']:
                        all_accuracies.append(weights['weights']['accuracy'])
        
        if not all_importances:
            print("  ✗ No valid feature importances found!")
            return None
        
        # Simple averaging (FedAvg with equal weights)
        # In production, you'd weight by number of training samples
        aggregated_importances = np.mean(all_importances, axis=0).tolist()
        
        # Calculate average accuracy (only if we have accuracy data)
        avg_accuracy = np.mean(all_accuracies) if all_accuracies else None
        
        self.aggregated_weights = {
            'fog_id': self.fog_id,
            'region_name': self.region_name,
            'num_edge_nodes': len(self.received_weights),
            'edge_intersections': self.edge_intersections,
            'aggregated_feature_importances': aggregated_importances,
            'average_accuracy': avg_accuracy,
            'timestamp': datetime.now().isoformat(),
            'aggregation_method': 'FedAvg'
        }
        
        print(f"  ✓ Aggregation complete!")
        print(f"    Aggregated from {len(self.received_weights)} Edge nodes")
        
        if avg_accuracy is not None:
            print(f"    Average accuracy: {avg_accuracy:.2%}")
        else:
            print(f"    Average accuracy: Not available")
        
        return self.aggregated_weights
    
    def get_aggregated_weights(self):
        """Return the aggregated weights"""
        return self.aggregated_weights
    
    def reset(self):
        """Reset for next round of federated learning"""
        self.received_weights = []
        self.aggregated_weights = None
        print(f"  ✓ Fog node {self.fog_id} reset for next round")
    
    def is_ready_to_aggregate(self):
        """Check if we've received weights from all Edge nodes in region"""
        return len(self.received_weights) >= len(self.edge_intersections)


class MultiFogManager:
    """
    Manages multiple Fog nodes
    """
    
    def __init__(self):
        self.fog_nodes = {}
        
        # Create Fog node for each region
        for fog_id, region_info in config.FOG_REGIONS.items():
            fog_node = FogAggregator(
                fog_id=fog_id,
                region_name=region_info['name'],
                edge_intersections=region_info['intersections']
            )
            self.fog_nodes[fog_id] = fog_node
    
    def route_edge_weights(self, edge_weights):
        """
        Route Edge weights to the appropriate Fog node
        """
        intersection_id = edge_weights.get('intersection_id')
        
        # Find which Fog region this intersection belongs to
        for fog_id, fog_node in self.fog_nodes.items():
            if intersection_id in fog_node.edge_intersections:
                fog_node.receive_edge_weights(edge_weights)
                return fog_id
        
        print(f"  ✗ No Fog node found for intersection {intersection_id}")
        return None
    
    def aggregate_all_regions(self):
        """
        Aggregate weights in all Fog regions
        """
        print("\n" + "="*70)
        print("AGGREGATING ALL FOG REGIONS")
        print("="*70)
        
        aggregated_results = {}
        
        for fog_id, fog_node in self.fog_nodes.items():
            if fog_node.is_ready_to_aggregate():
                result = fog_node.aggregate_weights_fedavg()
                aggregated_results[fog_id] = result
            else:
                print(f"\n  ⚠ {fog_id} not ready: {len(fog_node.received_weights)}/{len(fog_node.edge_intersections)} nodes")
        
        return aggregated_results


def test_fog_aggregator():
    """
    Test the Fog aggregator with simulated Edge weights
    """
    print("="*70)
    print("TESTING FOG AGGREGATOR")
    print("="*70)
    
    # Create Fog manager
    fog_manager = MultiFogManager()
    
    # Simulate Edge weights from different intersections
    print("\n" + "="*70)
    print("SIMULATING EDGE WEIGHTS")
    print("="*70)
    
    simulated_edge_weights = [
        # Downtown region (Fog 1)
        {'intersection_id': 1, 'weights': {'feature_importances': [0.25, 0.35, 0.25, 0.15], 'accuracy': 0.85}},
        {'intersection_id': 2, 'weights': {'feature_importances': [0.30, 0.30, 0.25, 0.15], 'accuracy': 0.87}},
        {'intersection_id': 3, 'weights': {'feature_importances': [0.28, 0.32, 0.23, 0.17], 'accuracy': 0.86}},
        {'intersection_id': 4, 'weights': {'feature_importances': [0.27, 0.33, 0.24, 0.16], 'accuracy': 0.88}},
        
        # Residential region (Fog 2)
        {'intersection_id': 5, 'weights': {'feature_importances': [0.20, 0.40, 0.25, 0.15], 'accuracy': 0.84}},
        {'intersection_id': 6, 'weights': {'feature_importances': [0.22, 0.38, 0.23, 0.17], 'accuracy': 0.83}},
        {'intersection_id': 7, 'weights': {'feature_importances': [0.21, 0.39, 0.24, 0.16], 'accuracy': 0.85}},
        
        # Outskirts region (Fog 3)
        {'intersection_id': 8, 'weights': {'feature_importances': [0.35, 0.25, 0.25, 0.15], 'accuracy': 0.82}},
        {'intersection_id': 9, 'weights': {'feature_importances': [0.33, 0.27, 0.23, 0.17], 'accuracy': 0.81}},
        {'intersection_id': 10, 'weights': {'feature_importances': [0.34, 0.26, 0.24, 0.16], 'accuracy': 0.83}},
    ]
    
    # Send weights to Fog nodes
    for edge_weight in simulated_edge_weights:
        fog_id = fog_manager.route_edge_weights(edge_weight)
        print(f"  → Routed to {fog_id}")
    
    # Aggregate all regions
    results = fog_manager.aggregate_all_regions()
    
    # Display results
    print("\n" + "="*70)
    print("AGGREGATION RESULTS")
    print("="*70)
    
    for fog_id, result in results.items():
        if result:
            print(f"\n{fog_id}:")
            print(f"  Region: {result['region_name']}")
            print(f"  Edge nodes: {result['num_edge_nodes']}")
            if result.get('average_accuracy') is not None:
                print(f"  Avg accuracy: {result['average_accuracy']:.2%}")
            print(f"  Feature importances: {result['aggregated_feature_importances']}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    return results


if __name__ == "__main__":
    test_fog_aggregator()