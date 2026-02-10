# simulation/traffic_simulator.py
import random
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

class TrafficSimulator:
    """
    Simulates traffic data for Nouakchott intersections
    """
    
    def __init__(self, intersection_id, intersection_name, lat, lon):
        self.intersection_id = intersection_id
        self.intersection_name = intersection_name
        self.lat = lat
        self.lon = lon
        self.current_state = 'Fluide'
        
    def get_time_factor(self, current_hour):
        """
        Traffic varies by time of day
        """
        if 7 <= current_hour < 9 or 17 <= current_hour < 19:
            return 1.5  # Rush hour
        elif 12 <= current_hour < 14:
            return 1.2  # Lunch time
        elif 22 <= current_hour or current_hour < 6:
            return 0.3  # Night
        else:
            return 1.0
    
    def determine_traffic_state(self, vehicle_count, avg_speed):
        """
        Determine traffic state based on vehicle count and speed
        """
        if vehicle_count < 20 and avg_speed > 40:
            return 'Fluide'
        elif vehicle_count > 50 or avg_speed < 15:
            return 'Bloqué'
        else:
            return 'Dense'
    
    def generate_traffic_data(self, timestamp=None):
        """
        Generate one data point for this intersection
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        current_hour = timestamp.hour
        time_factor = self.get_time_factor(current_hour)
        
        # Base values with randomness
        base_vehicle_count = random.randint(10, 40)
        base_speed = random.uniform(20, 60)
        
        # Apply time factor
        vehicle_count = int(base_vehicle_count * time_factor)
        
        # Speed decreases with more vehicles
        if vehicle_count > 40:
            avg_speed = base_speed * 0.5
        elif vehicle_count > 25:
            avg_speed = base_speed * 0.7
        else:
            avg_speed = base_speed
        
        # Add noise
        avg_speed = max(5, avg_speed + random.uniform(-10, 10))
        vehicle_count = max(0, vehicle_count + random.randint(-5, 5))
        
        # Calculate density
        num_lanes = 2
        density = vehicle_count / num_lanes
        
        # Determine state
        traffic_state = self.determine_traffic_state(vehicle_count, avg_speed)
        self.current_state = traffic_state
        
        # Create data point
        data_point = {
            'timestamp': timestamp.isoformat(),
            'intersection_id': self.intersection_id,
            'intersection_name': self.intersection_name,
            'latitude': self.lat,
            'longitude': self.lon,
            'vehicle_count': vehicle_count,
            'avg_speed_kmh': round(avg_speed, 2),
            'density': round(density, 2),
            'num_lanes': num_lanes,
            'traffic_state': traffic_state,
            'hour': current_hour
        }
        
        return data_point


class MultiIntersectionSimulator:
    """
    Manages multiple intersections and generates data for all
    """
    
    def __init__(self):
        self.simulators = []
        
        # Create a simulator for each intersection
        for intersection in config.INTERSECTIONS:
            sim = TrafficSimulator(
                intersection_id=intersection['id'],
                intersection_name=intersection['name'],
                lat=intersection['lat'],
                lon=intersection['lon']
            )
            self.simulators.append(sim)
    
    def generate_batch_data(self, timestamp=None):
        """
        Generate data for ALL intersections at once
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        batch_data = []
        for simulator in self.simulators:
            data = simulator.generate_traffic_data(timestamp)
            batch_data.append(data)
        
        return batch_data
    
    def simulate_time_series(self, duration_hours=1, interval_seconds=5):
        """
        Generate time series data
        """
        all_data = []
        start_time = datetime.now()
        
        total_points = int((duration_hours * 3600) / interval_seconds)
        
        print(f"Simulating {duration_hours} hour(s) of traffic data...")
        print(f"Generating {total_points} data points per intersection...")
        
        for i in range(total_points):
            current_time = start_time + timedelta(seconds=i * interval_seconds)
            batch = self.generate_batch_data(current_time)
            all_data.extend(batch)
            
            # Progress indicator
            if (i + 1) % 100 == 0:
                progress = ((i + 1) / total_points) * 100
                print(f"Progress: {progress:.1f}% ({i + 1}/{total_points} batches)")
        
        return pd.DataFrame(all_data)
    
    def save_to_csv(self, df, filename):
        """Save data to CSV file"""
        filepath = f"data/simulated/{filename}"
        df.to_csv(filepath, index=False)
        print(f"\n✓ Data saved to: {filepath}")
        print(f"  Total records: {len(df)}")
        return filepath
    
    def save_to_json(self, df, filename):
        """Save data to JSON file"""
        filepath = f"data/simulated/{filename}"
        df.to_json(filepath, orient='records', indent=2)
        print(f"✓ Data saved to: {filepath}")
        return filepath


def main():
    """
    Main function to run the simulator
    """
    print("=" * 60)
    print("TRAFFIC SIMULATOR - NOUAKCHOTT")
    print("=" * 60)
    
    # Create simulator
    sim = MultiIntersectionSimulator()
    
    # Generate 1 hour of data, one data point every 5 seconds
    df = sim.simulate_time_series(duration_hours=1, interval_seconds=5)
    
    # Display sample
    print("\n" + "=" * 60)
    print("SAMPLE DATA (first 5 rows):")
    print("=" * 60)
    print(df.head())
    
    # Statistics
    print("\n" + "=" * 60)
    print("TRAFFIC STATISTICS:")
    print("=" * 60)
    print(df['traffic_state'].value_counts())
    print("\nAverage speed by state:")
    print(df.groupby('traffic_state')['avg_speed_kmh'].mean())
    
    # Save data
    print("\n" + "=" * 60)
    print("SAVING DATA:")
    print("=" * 60)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    sim.save_to_csv(df, f"traffic_data_{timestamp_str}.csv")
    sim.save_to_json(df, f"traffic_data_{timestamp_str}.json")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE!")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    df = main()