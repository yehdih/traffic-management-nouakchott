# config.py
import os

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SIMULATED_DATA_DIR = os.path.join(DATA_DIR, 'simulated')
MODELS_DIR = os.path.join(DATA_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_TOPIC_EDGE_TO_FOG = 'edge-to-fog'
KAFKA_TOPIC_FOG_TO_CLOUD = 'fog-to-cloud'
KAFKA_TOPIC_CLOUD_TO_EDGE = 'cloud-to-edge'

# Simulation Parameters
NUM_INTERSECTIONS = 10  # Number of traffic intersections
SIMULATION_DURATION = 3600  # 1 hour in seconds
DATA_GENERATION_INTERVAL = 5  # Generate data every 5 seconds

# Nouakchott Major Roads (Examples)
INTERSECTIONS = [
    {"id": 1, "name": "Avenue Charles de Gaulle - Rue 42-044", "lat": 18.0735, "lon": -15.9582},
    {"id": 2, "name": "Avenue Gamal Abdel Nasser - Rue Mamadou Konaté", "lat": 18.0865, "lon": -15.9750},
    {"id": 3, "name": "Route de Rosso - Avenue Kennedy", "lat": 18.0912, "lon": -15.9623},
    {"id": 4, "name": "Avenue de l'Indépendance - Rue 42-252", "lat": 18.0795, "lon": -15.9685},
    {"id": 5, "name": "Carrefour Madrid - Tevragh Zeina", "lat": 18.1012, "lon": -15.9456},
    {"id": 6, "name": "Route de l'Espoir - Entrée Ksar", "lat": 18.0654, "lon": -15.9812},
    {"id": 7, "name": "Avenue Moktar Ould Daddah - Marché Capitale", "lat": 18.0823, "lon": -15.9734},
    {"id": 8, "name": "Ilot C - Carrefour Mosquée Saoudienne", "lat": 18.1123, "lon": -15.9523},
    {"id": 9, "name": "Route Nouadhibou - Sortie Nord", "lat": 18.1234, "lon": -15.9645},
    {"id": 10, "name": "Carrefour PK7 - Route de Boutilimit", "lat": 18.0512, "lon": -15.9923}
]

# Traffic States
TRAFFIC_STATES = ['Fluide', 'Dense', 'Bloqué']

# Federated Learning Parameters
FEDERATED_ROUNDS = 10
EDGE_NODES_PER_FOG = 3
NUM_FOG_NODES = 3

# Model Parameters
RANDOM_SEED = 42


# Fog Layer Configuration
FOG_REGIONS = {
    'fog_1_downtown': {
        'name': 'Downtown Nouakchott',
        'intersections': [1, 2, 3, 4]
    },
    'fog_2_residential': {
        'name': 'Residential Areas',
        'intersections': [5, 6, 7]
    },
    'fog_3_outskirts': {
        'name': 'City Outskirts',
        'intersections': [8, 9, 10]
    }
}