# simulation/analyze_traffic.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_latest_simulation():
    """
    Analyze the most recent simulation data
    """
    # Find the latest CSV file
    sim_dir = "data/simulated"
    files = [f for f in os.listdir(sim_dir) if f.endswith('.csv')]
    
    if not files:
        print("No simulation data found! Run traffic_simulator.py first.")
        return
    
    latest_file = max(files)
    filepath = os.path.join(sim_dir, latest_file)
    
    print(f"Analyzing: {latest_file}\n")
    
    # Load data
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Traffic Analysis - Nouakchott', fontsize=16, fontweight='bold')
    
    # 1. Traffic state distribution
    ax1 = axes[0, 0]
    df['traffic_state'].value_counts().plot(kind='bar', ax=ax1, color=['green', 'orange', 'red'])
    ax1.set_title('Distribution of Traffic States')
    ax1.set_xlabel('Traffic State')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=0)
    
    # 2. Average speed by hour
    ax2 = axes[0, 1]
    hourly_speed = df.groupby('hour')['avg_speed_kmh'].mean()
    hourly_speed.plot(kind='line', ax=ax2, marker='o', color='blue')
    ax2.set_title('Average Speed by Hour of Day')
    ax2.set_xlabel('Hour')
    ax2.set_ylabel('Speed (km/h)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Vehicle count by hour
    ax3 = axes[1, 0]
    hourly_vehicles = df.groupby('hour')['vehicle_count'].mean()
    hourly_vehicles.plot(kind='line', ax=ax3, marker='s', color='purple')
    ax3.set_title('Average Vehicle Count by Hour')
    ax3.set_xlabel('Hour')
    ax3.set_ylabel('Vehicle Count')
    ax3.grid(True, alpha=0.3)
    
    # 4. Speed vs Vehicle Count (scatter)
    ax4 = axes[1, 1]
    colors = {'Fluide': 'green', 'Dense': 'orange', 'Bloqué': 'red'}
    for state in df['traffic_state'].unique():
        mask = df['traffic_state'] == state
        ax4.scatter(df[mask]['vehicle_count'], 
                   df[mask]['avg_speed_kmh'],
                   label=state, 
                   color=colors[state],
                   alpha=0.5)
    ax4.set_title('Speed vs Vehicle Count')
    ax4.set_xlabel('Vehicle Count')
    ax4.set_ylabel('Speed (km/h)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    plot_path = f"data/simulated/analysis_{latest_file.replace('.csv', '.png')}"
    plt.savefig(plot_path, dpi=150)
    print(f"✓ Analysis plot saved: {plot_path}")
    
    plt.show()
    
    # Print statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS:")
    print("=" * 60)
    print(df[['vehicle_count', 'avg_speed_kmh', 'density']].describe())
    
    print("\n" + "=" * 60)
    print("TRAFFIC STATE DISTRIBUTION:")
    print("=" * 60)
    print(df['traffic_state'].value_counts(normalize=True) * 100)

if __name__ == "__main__":
    analyze_latest_simulation()