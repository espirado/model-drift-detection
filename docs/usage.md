# Usage Guide

This guide explains how to use the System Reliability Drift Detection project for monitoring system reliability using log data.

## Basic Usage

### 1. Log Ingestion

The system can ingest logs from various sources:

```python
from src.ingestion.log_loader import LogLoader

# Load logs from a file
loader = LogLoader()
loader.load_from_file("data/raw/HDFS/HDFS.log")

# Stream logs to Kafka
loader.stream_to_kafka(topic="hdfs_logs")
```

### 2. Log Parsing

Parse logs into structured formats:

```python
from src.parsing.log_parser import LogParser

# Initialize parser
parser = LogParser()

# Parse logs
parsed_logs = parser.parse("data/raw/HDFS/HDFS.log")

# Save parsed logs
parser.save_parsed_logs(parsed_logs, "data/processed/HDFS_parsed.csv")
```

### 3. Feature Extraction

Extract features from parsed logs:

```python
from src.parsing.feature_extractor import FeatureExtractor

# Initialize feature extractor
extractor = FeatureExtractor()

# Extract features
features = extractor.extract(parsed_logs)

# Save features
extractor.save_features(features, "data/processed/HDFS_features.csv")
```

### 4. Drift Detection

Detect drift in log patterns:

```python
from src.detection.distribution_drift import DistributionDriftDetector
from src.detection.error_rate_drift import ErrorRateDriftDetector

# Initialize detectors
dist_detector = DistributionDriftDetector()
error_detector = ErrorRateDriftDetector()

# Detect distribution drift
dist_drift = dist_detector.detect(features)

# Detect error rate drift
error_drift = error_detector.detect(parsed_logs)

# Get drift alerts
alerts = dist_detector.get_alerts() + error_detector.get_alerts()
```

### 5. Visualization

Visualize drift detection results:

```python
from src.visualization.dashboard import Dashboard
from src.visualization.metrics_visualizer import MetricsVisualizer

# Initialize visualizers
dashboard = Dashboard()
visualizer = MetricsVisualizer()

# Create dashboard
dashboard.create()

# Visualize metrics
visualizer.plot_error_rate(parsed_logs)
visualizer.plot_distribution_drift(dist_drift)
```

## Advanced Usage

### Custom Log Parsing

Create a custom log parser for specific log formats:

```python
from src.parsing.log_parser import BaseLogParser

class CustomLogParser(BaseLogParser):
    def parse_line(self, line):
        # Custom parsing logic
        parts = line.split("|")
        return {
            "timestamp": parts[0],
            "component": parts[1],
            "severity": parts[2],
            "message": parts[3]
        }

# Use custom parser
parser = CustomLogParser()
parsed_logs = parser.parse("data/raw/custom_logs.log")
```

### Custom Drift Detection

Implement a custom drift detection algorithm:

```python
from src.detection.distribution_drift import BaseDriftDetector

class CustomDriftDetector(BaseDriftDetector):
    def detect(self, data):
        # Custom drift detection logic
        # ...
        return drift_results

# Use custom detector
detector = CustomDriftDetector()
drift = detector.detect(features)
```

### Real-time Monitoring

Set up real-time monitoring of system logs:

```python
from src.ingestion.kafka_producer import KafkaProducer
from src.detection.pattern_drift import PatternDriftDetector
from src.visualization.alert_manager import AlertManager

# Initialize components
producer = KafkaProducer()
detector = PatternDriftDetector()
alert_manager = AlertManager()

# Set up real-time monitoring
def process_log(log):
    # Process incoming log
    parsed_log = parser.parse_line(log)
    
    # Detect drift
    drift = detector.detect_incremental(parsed_log)
    
    # Send alert if drift detected
    if drift.is_drift_detected:
        alert_manager.send_alert(drift)

# Start monitoring
producer.consume_topic("system_logs", process_log)
```

## Configuration

### Kafka Configuration

Edit `config/kafka_config.yaml`:

```yaml
kafka:
  bootstrap_servers: localhost:9092
  topics:
    hdfs_logs: hdfs_logs
    apache_logs: apache_logs
    healthapp_logs: healthapp_logs
    ssh_logs: ssh_logs
```

### Drift Detection Configuration

Edit `config/detection_config.yaml`:

```yaml
detection:
  window_size: 1000
  threshold: 0.05
  methods:
    distribution:
      enabled: true
      algorithm: jensen_shannon
    error_rate:
      enabled: true
      min_errors: 5
    pattern:
      enabled: true
      similarity_threshold: 0.8
```

### Visualization Configuration

Edit `config/visualization_config.yaml`:

```yaml
visualization:
  dashboard:
    port: 8050
    refresh_interval: 5
  alerts:
    email:
      enabled: true
      recipients: ["admin@example.com"]
    slack:
      enabled: false
      webhook_url: ""
```

## Examples

### Example 1: Monitor HDFS Logs for Anomalies

```python
# Load and parse HDFS logs
loader = LogLoader()
parser = LogParser()
logs = loader.load_from_file("data/raw/HDFS/HDFS.log")
parsed_logs = parser.parse(logs)

# Extract features
extractor = FeatureExtractor()
features = extractor.extract(parsed_logs)

# Detect anomalies
detector = AnomalyDetector()
anomalies = detector.detect(features)

# Visualize results
visualizer = MetricsVisualizer()
visualizer.plot_anomalies(anomalies)
```

### Example 2: Real-time Apache Server Monitoring

```python
# Set up Kafka producer
producer = KafkaProducer()

# Set up drift detector
detector = ErrorRateDriftDetector()

# Set up alert manager
alert_manager = AlertManager()

# Process incoming logs
def process_apache_log(log):
    parsed_log = parser.parse_line(log)
    drift = detector.detect_incremental(parsed_log)
    if drift.is_drift_detected:
        alert_manager.send_alert(drift)

# Start monitoring
producer.consume_topic("apache_logs", process_apache_log)
```

## Best Practices

1. **Log Sampling**: For large log volumes, consider sampling to reduce processing load
2. **Baseline Establishment**: Establish a good baseline before monitoring for drift
3. **Threshold Tuning**: Adjust detection thresholds based on your specific system
4. **Alert Management**: Configure alerts to avoid notification fatigue
5. **Performance Optimization**: Use batch processing for large log volumes 