# simulation/realtime_simulator.py
import time
import json
from datetime import datetime
from simulation.traffic_simulator import MultiIntersectionSimulator

class RealtimeTrafficSimulator:
    """
    Generates traffic data in real-time
    Useful for testing Kafka streaming
    """
    
    def __init__(self, interval_seconds=5):
        self.simulator = MultiIntersectionSimulator()
        self.interval = interval_seconds
        self.running = False
    
    def start(self, duration_seconds=None):
        """
        Start generating data continuously
        
        Args:
            duration_seconds: Run for X seconds (None = infinite)
        """
        self.running = True
        start_time = time.time()
        iteration = 0
        
        print(f"Starting real-time simulation (interval: {self.interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                # Generate batch
                batch = self.simulator.generate_batch_data()
                
                # Display (in real scenario, this would go to Kafka)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Generated {len(batch)} data points (iteration {iteration + 1})")
                
                # Show sample from one intersection
                sample = batch[0]
                print(f"  Sample: {sample['intersection_name']}")
                print(f"    State: {sample['traffic_state']}, Speed: {sample['avg_speed_kmh']} km/h, Vehicles: {sample['vehicle_count']}")
                print()
                
                iteration += 1
                
                # Check duration
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                
                # Wait
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        
        self.running = False
        print(f"\nTotal iterations: {iteration}")
    
    def stop(self):
        """Stop the simulation"""
        self.running = False


if __name__ == "__main__":
    # Run for 60 seconds (or press Ctrl+C to stop)
    sim = RealtimeTrafficSimulator(interval_seconds=5)
    sim.start(duration_seconds=60)