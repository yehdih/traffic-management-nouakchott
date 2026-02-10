# Federated Learning with Kafka and Spark

This project demonstrates distributed machine learning using Federated Learning, Apache Kafka for messaging, and Apache Spark for stream processing.

## Architecture

- **Device Layer**: Simulated IoT sensors generating temperature and vibration data
- **Fog Layer**: Local Spark nodes training models on streaming data
- **Cloud Layer**: Central aggregator combining models using Federated Averaging

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Start Kafka: `docker-compose up -d`
3. Create topics (see commands in documentation)
4. Run components in order:
   - Producers
   - Fog nodes
   - Aggregator

## Technologies

- Python 3.8+
- Apache Kafka
- Apache Spark (PySpark)
- Docker

## Project Structure
```
federated-learning-project/
├── producers/       # Sensor simulators
├── fog_nodes/       # Local training nodes
├── cloud/          # Model aggregator
├── models/         # ML model definitions
├── utils/          # Helper functions
├── dashboard/      # Monitoring
└── logs/           # Application logs
```

## Status

🚧 In Development
```

4. Save

---

## **Part F: Your Current Project Structure**

Your VS Code Explorer should now show:
```
federated-learning-project/
├── .gitignore
├── docker-compose.yml
├── README.md
├── requirements.txt
├── test_imports.py
├── cloud/
├── dashboard/
├── fog_nodes/
├── logs/
├── models/
├── producers/
└── utils/