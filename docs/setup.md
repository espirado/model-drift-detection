# Setup Guide

This guide will help you set up the System Reliability Drift Detection project.

## Prerequisites

- Python 3.8 or higher
- Apache Kafka
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/model-drift-detection.git
cd model-drift-detection
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Log Datasets

Download the log datasets from Loghub:

```bash
# Create data directories
mkdir -p data/raw data/processed

# Download HDFS logs
wget https://zenodo.org/records/8196385/files/HDFS.tar.gz?download=1 -O data/raw/HDFS.tar.gz
tar -xzf data/raw/HDFS.tar.gz -C data/raw/

# Download Apache logs
wget https://zenodo.org/records/8196385/files/Apache.tar.gz?download=1 -O data/raw/Apache.tar.gz
tar -xzf data/raw/Apache.tar.gz -C data/raw/

# Download HealthApp logs
wget https://zenodo.org/records/8196385/files/HealthApp.tar.gz?download=1 -O data/raw/HealthApp.tar.gz
tar -xzf data/raw/HealthApp.tar.gz -C data/raw/

# Download OpenSSH logs
wget https://zenodo.org/records/8196385/files/SSH.tar.gz?download=1 -O data/raw/OpenSSH.tar.gz
tar -xzf data/raw/OpenSSH.tar.gz -C data/raw/
```

### 5. Set Up Apache Kafka

#### Using Docker (Recommended)

```bash
# Start Zookeeper
docker run -d --name zookeeper -p 2181:2181 wurstmeister/zookeeper

# Start Kafka
docker run -d --name kafka -p 9092:9092 \
  -e KAFKA_ADVERTISED_HOST_NAME=localhost \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  wurstmeister/kafka
```

#### Manual Installation

1. Download Kafka from [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads)
2. Extract the archive
3. Start Zookeeper: `bin/zookeeper-server-start.sh config/zookeeper.properties`
4. Start Kafka: `bin/kafka-server-start.sh config/server.properties`

### 6. Configure the Project

Edit the configuration files in the `config/` directory to match your environment:

- `kafka_config.yaml`: Set your Kafka broker address and topic names
- `detection_config.yaml`: Adjust drift detection parameters
- `visualization_config.yaml`: Configure dashboard settings

## Running the Project

### 1. Start the Log Ingestion

```bash
python src/ingestion/log_loader.py --dataset HDFS
```

### 2. Start the Drift Detection

```bash
python src/detection/distribution_drift.py
```

### 3. Launch the Dashboard

```bash
python src/visualization/dashboard.py
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Kafka Connection Errors**
   - Ensure Kafka is running: `docker ps` or check Kafka logs
   - Verify the broker address in `config/kafka_config.yaml`

2. **Log Parsing Errors**
   - Check log format compatibility
   - Verify log file paths in configuration

3. **Memory Issues**
   - Reduce batch size in configuration
   - Process smaller log chunks

## Next Steps

- Explore the [Usage Guide](usage.md) for detailed examples
- Check the [Project Structure](project_structure.md) for an overview of the codebase
- Contribute to the project by following the contribution guidelines 