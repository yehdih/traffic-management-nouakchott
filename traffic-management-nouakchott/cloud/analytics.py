# cloud/analytics.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class CloudAnalytics:
    """
    Analytics and monitoring for the Cloud server
    """
    
    def __init__(self):
        self.training_history = []
    
    def load_training_history(self, history):
        """
        Load training history from Cloud server
        """
        self.training_history = history
    
    def calculate_metrics(self):
        """
        Calculate key performance metrics
        """
        if not self.training_history:
            return None
        
        metrics = {
            'total_rounds': len(self.training_history),
            'final_accuracy': self.training_history[-1]['global_accuracy'],
            'initial_accuracy': self.training_history[0]['global_accuracy'],
            'improvement': self.training_history[-1]['global_accuracy'] - self.training_history[0]['global_accuracy'],
            'average_accuracy': np.mean([r['global_accuracy'] for r in self.training_history]),
            'total_edge_nodes': self.training_history[-1]['num_edge_nodes_total']
        }
        
        return metrics
    
    def plot_training_progress(self, save_path=None):
        """
        Plot training progress over rounds
        """
        if not self.training_history:
            print("No training history to plot")
            return
        
        rounds = [r['round'] for r in self.training_history]
        accuracies = [r['global_accuracy'] * 100 for r in self.training_history]
        
        plt.figure(figsize=(10, 6))
        plt.plot(rounds, accuracies, marker='o', linewidth=2, markersize=8)
        plt.xlabel('Federated Learning Round', fontsize=12)
        plt.ylabel('Global Accuracy (%)', fontsize=12)
        plt.title('Federated Learning Training Progress', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"✓ Plot saved: {save_path}")
        
        plt.show()
    
    def plot_feature_importance_evolution(self, save_path=None):
        """
        Plot how feature importances change over rounds
        """
        if not self.training_history:
            print("No training history to plot")
            return
        
        feature_names = ['Vehicle Count', 'Avg Speed', 'Density', 'Hour']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, feature in enumerate(feature_names):
            importances = [r['global_feature_importances'][i] for r in self.training_history]
            rounds = [r['round'] for r in self.training_history]
            ax.plot(rounds, importances, marker='o', label=feature, linewidth=2)
        
        ax.set_xlabel('Federated Learning Round', fontsize=12)
        ax.set_ylabel('Feature Importance', fontsize=12)
        ax.set_title('Feature Importance Evolution', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"✓ Plot saved: {save_path}")
        
        plt.show()
    
    def generate_report(self, save_path=None):
        """
        Generate a comprehensive text report
        """
        if not self.training_history:
            print("No training history to report")
            return
        
        metrics = self.calculate_metrics()
        
        report = []
        report.append("=" * 70)
        report.append("FEDERATED LEARNING ANALYTICS REPORT")
        report.append("=" * 70)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n{'='*70}")
        report.append("SUMMARY METRICS")
        report.append("=" * 70)
        report.append(f"\nTotal Training Rounds: {metrics['total_rounds']}")
        report.append(f"Total Edge Nodes: {metrics['total_edge_nodes']}")
        report.append(f"\nInitial Accuracy: {metrics['initial_accuracy']:.2%}")
        report.append(f"Final Accuracy: {metrics['final_accuracy']:.2%}")
        report.append(f"Improvement: {metrics['improvement']:+.2%}")
        report.append(f"Average Accuracy: {metrics['average_accuracy']:.2%}")
        
        report.append(f"\n{'='*70}")
        report.append("ROUND-BY-ROUND DETAILS")
        report.append("=" * 70)
        
        for round_data in self.training_history:
            report.append(f"\nRound {round_data['round']}:")
            report.append(f"  Accuracy: {round_data['global_accuracy']:.2%}")
            report.append(f"  Feature Importances: {round_data['global_feature_importances']}")
            report.append(f"  Regions: {', '.join(round_data['fog_regions'])}")
        
        report.append(f"\n{'='*70}")
        report.append("END OF REPORT")
        report.append("=" * 70)
        
        report_text = '\n'.join(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
            print(f"✓ Report saved: {save_path}")
        
        print(report_text)
        
        return report_text


def test_analytics():
    """
    Test analytics with sample data
    """
    # Simulate training history
    sample_history = [
        {
            'round': 0,
            'global_accuracy': 0.82,
            'global_feature_importances': [0.25, 0.35, 0.25, 0.15],
            'num_edge_nodes_total': 10,
            'fog_regions': ['Downtown', 'Residential', 'Outskirts']
        },
        {
            'round': 1,
            'global_accuracy': 0.85,
            'global_feature_importances': [0.27, 0.33, 0.24, 0.16],
            'num_edge_nodes_total': 10,
            'fog_regions': ['Downtown', 'Residential', 'Outskirts']
        },
        {
            'round': 2,
            'global_accuracy': 0.87,
            'global_feature_importances': [0.28, 0.32, 0.24, 0.16],
            'num_edge_nodes_total': 10,
            'fog_regions': ['Downtown', 'Residential', 'Outskirts']
        }
    ]
    
    analytics = CloudAnalytics()
    analytics.load_training_history(sample_history)
    
    # Generate report
    analytics.generate_report('data/models/fl_report.txt')
    
    # Plot progress
    analytics.plot_training_progress('data/models/training_progress.png')
    
    # Plot feature importance
    analytics.plot_feature_importance_evolution('data/models/feature_importance.png')


if __name__ == "__main__":
    test_analytics()