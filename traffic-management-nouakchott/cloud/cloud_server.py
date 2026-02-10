# cloud/cloud_server.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
from datetime import datetime
from collections import defaultdict
import config

class CloudFederatedServer:
    """
    Central Cloud server for Federated Learning
    
    Responsibilities:
    1. Receive aggregated weights from all Fog nodes
    2. Perform global FedAvg
    3. Create unified global model
    4. Distribute global model back to Edge
    """
    
    def __init__(self):
        self.fog_weights = []  # Store weights from all Fog nodes
        self.global_model = None
        self.training_rounds = []  # History of training rounds
        self.current_round = 0
        
        print("="*70)
        print("CLOUD FEDERATED LEARNING SERVER INITIALIZED")
        print("="*70)
    
    def receive_fog_weights(self, fog_data):
        """
        Receive aggregated weights from a Fog node
        
        Args:
            fog_data: dict containing aggregated weights from Fog
        """
        fog_id = fog_data['fog_id']
        aggregated = fog_data['aggregated_weights']
        
        self.fog_weights.append(aggregated)
        
        print(f"\n✓ Received from {fog_id}")
        print(f"  Region: {aggregated['region_name']}")
        print(f"  Edge nodes: {aggregated['num_edge_nodes']}")
        
        # Handle None accuracy gracefully
        if aggregated.get('average_accuracy') is not None:
            print(f"  Avg accuracy: {aggregated['average_accuracy']:.2%}")
        else:
            print(f"  Avg accuracy: Not available")
        
        print(f"  Progress: {len(self.fog_weights)}/{len(config.FOG_REGIONS)} Fog nodes")
        
        return True
    
    def is_ready_for_global_aggregation(self):
        """
        Check if we've received weights from all Fog nodes
        """
        return len(self.fog_weights) >= len(config.FOG_REGIONS)
    
    def global_fedavg(self):
        """
        Perform global FedAvg across all Fog nodes
        
        Global FedAvg formula:
        w_global = Σ(n_r / N_total) * w_r
        
        where:
        - w_r = aggregated weights from Fog region r
        - n_r = number of Edge nodes in region r
        - N_total = total Edge nodes across all regions
        """
        
        if not self.fog_weights:
            print("✗ No Fog weights received!")
            return None
        
        print("\n" + "="*70)
        print("PERFORMING GLOBAL FEDAVG")
        print("="*70)
        
        # Extract feature importances from all Fog nodes
        all_importances = []
        all_weights_per_region = []  # Number of Edge nodes per region
        all_accuracies = []
        
        for fog_data in self.fog_weights:
            importances = fog_data['aggregated_feature_importances']
            num_nodes = fog_data['num_edge_nodes']
            accuracy = fog_data.get('average_accuracy')  # Use .get() for safety
            
            all_importances.append(importances)
            all_weights_per_region.append(num_nodes)
            
            # Only add accuracy if it's not None
            if accuracy is not None:
                all_accuracies.append(accuracy)
        
        # Calculate total nodes
        total_nodes = sum(all_weights_per_region)
        
        # Weighted average based on number of Edge nodes per region
        weighted_importances = []
        for importances, num_nodes in zip(all_importances, all_weights_per_region):
            weight = num_nodes / total_nodes
            weighted = np.array(importances) * weight
            weighted_importances.append(weighted)
        
        # Global aggregated importances
        global_importances = np.sum(weighted_importances, axis=0).tolist()
        
        # Global average accuracy (only if we have accuracy data)
        if all_accuracies:
            # Weight by number of nodes per region that have accuracy
            weights_with_acc = [all_weights_per_region[i] for i in range(len(self.fog_weights)) 
                               if self.fog_weights[i].get('average_accuracy') is not None]
            global_accuracy = np.average(all_accuracies, weights=weights_with_acc)
        else:
            global_accuracy = None
        
        # Create global model
        self.global_model = {
            'round': self.current_round,
            'global_feature_importances': global_importances,
            'global_accuracy': global_accuracy,
            'num_fog_nodes': len(self.fog_weights),
            'num_edge_nodes_total': total_nodes,
            'fog_regions': [f['region_name'] for f in self.fog_weights],
            'timestamp': datetime.now().isoformat(),
            'aggregation_method': 'Global FedAvg'
        }
        
        print(f"\n✓ Global aggregation complete!")
        print(f"  Round: {self.current_round}")
        print(f"  Total Edge nodes: {total_nodes}")
        
        if global_accuracy is not None:
            print(f"  Global accuracy: {global_accuracy:.2%}")
        else:
            print(f"  Global accuracy: Not available")
        
        print(f"  Global feature importances: {global_importances}")
        
        # Save to history
        self.training_rounds.append(self.global_model.copy())
        
        return self.global_model
    
    def get_global_model(self):
        """
        Get the current global model
        """
        return self.global_model
    
    def prepare_model_for_distribution(self):
        """
        Prepare global model to send back to Edge nodes
        """
        if not self.global_model:
            return None
        
        distribution_package = {
            'global_model': self.global_model,
            'message_type': 'global_model_update',
            'timestamp': datetime.now().isoformat(),
            'instructions': 'Update local models with global weights'
        }
        
        return distribution_package
    
    def reset_for_next_round(self):
        """
        Reset for next federated learning round
        """
        self.fog_weights = []
        self.current_round += 1
        
        print(f"\n✓ Cloud server reset for round {self.current_round}")
    
    def get_training_history(self):
        """
        Get complete training history
        """
        return self.training_rounds
    
    def print_statistics(self):
        """
        Print overall statistics
        """
        if not self.training_rounds:
            print("No training history yet")
            return
        
        print("\n" + "="*70)
        print("TRAINING STATISTICS")
        print("="*70)
        
        print(f"\nTotal rounds completed: {len(self.training_rounds)}")
        
        print("\nAccuracy progression:")
        for i, round_data in enumerate(self.training_rounds):
            if round_data.get('global_accuracy') is not None:
                print(f"  Round {round_data['round']}: {round_data['global_accuracy']:.2%}")
            else:
                print(f"  Round {round_data['round']}: Not available")
        
        # Calculate improvement if we have accuracy data
        accuracies = [r['global_accuracy'] for r in self.training_rounds if r.get('global_accuracy') is not None]
        
        if len(accuracies) > 1:
            first_acc = accuracies[0]
            last_acc = accuracies[-1]
            improvement = last_acc - first_acc
            print(f"\nTotal improvement: {improvement:+.2%}")


def test_cloud_server():
    """
    Test the Cloud server with simulated Fog data
    """
    print("="*70)
    print("TESTING CLOUD FEDERATED SERVER")
    print("="*70)
    
    # Create Cloud server
    cloud = CloudFederatedServer()
    
    # Simulate Fog aggregated weights
    simulated_fog_data = [
        {
            'fog_id': 'fog_1_downtown',
            'aggregated_weights': {
                'fog_id': 'fog_1_downtown',
                'region_name': 'Downtown Nouakchott',
                'num_edge_nodes': 4,
                'aggregated_feature_importances': [0.275, 0.325, 0.242, 0.158],
                'average_accuracy': 0.865,
                'timestamp': datetime.now().isoformat()
            }
        },
        {
            'fog_id': 'fog_2_residential',
            'aggregated_weights': {
                'fog_id': 'fog_2_residential',
                'region_name': 'Residential Areas',
                'num_edge_nodes': 3,
                'aggregated_feature_importances': [0.210, 0.390, 0.240, 0.160],
                'average_accuracy': 0.840,
                'timestamp': datetime.now().isoformat()
            }
        },
        {
            'fog_id': 'fog_3_outskirts',
            'aggregated_weights': {
                'fog_id': 'fog_3_outskirts',
                'region_name': 'City Outskirts',
                'num_edge_nodes': 3,
                'aggregated_feature_importances': [0.340, 0.260, 0.240, 0.160],
                'average_accuracy': 0.820,
                'timestamp': datetime.now().isoformat()
            }
        }
    ]
    
    # Send Fog weights to Cloud
    print("\n" + "="*70)
    print("RECEIVING FOG WEIGHTS")
    print("="*70)
    
    for fog_data in simulated_fog_data:
        cloud.receive_fog_weights(fog_data)
    
    # Perform global aggregation
    if cloud.is_ready_for_global_aggregation():
        global_model = cloud.global_fedavg()
        
        # Prepare for distribution
        print("\n" + "="*70)
        print("PREPARING GLOBAL MODEL FOR DISTRIBUTION")
        print("="*70)
        
        distribution = cloud.prepare_model_for_distribution()
        print(json.dumps(distribution, indent=2))
        
        # Statistics
        cloud.print_statistics()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    
    return cloud


if __name__ == "__main__":
    test_cloud_server()