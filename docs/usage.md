# Usage Guide

This guide provides detailed instructions for using the Model Drift Detection system for analyzing system logs and detecting drift patterns.

## Data Processing Workflow

### 1. Data Preprocessing

The preprocessing phase converts raw logs into structured data suitable for analysis:

```python
from src.preprocessing import log_processor
from src.config import config

# Initialize processor
processor = log_processor.LogProcessor(config.get_config())

# Process logs
processed_data = processor.process_logs(
    log_type="HDFS",  # Options: HDFS, Apache, HealthApp, BGL, HPC, Linux, Mac
    input_path="datasets/raw_drift_dataset/HDFS",
    output_path="datasets/processed/hdfs_processed.csv"
)
```

### 2. Feature Engineering

Extract relevant features from processed logs:

```python
from src.features import feature_extractor

# Initialize feature extractor
extractor = feature_extractor.LogFeatureExtractor()

# Extract features
features = extractor.extract_features(
    processed_data,
    time_window='1H',  # Options: '1H', '1D', '1W'
    include_patterns=True,
    include_components=True
)
```

### 3. Drift Detection

Implement drift detection on extracted features:

```python
from src.detection import drift_detector

# Initialize detector
detector = drift_detector.DriftDetector(
    baseline_period='7D',
    detection_window='1D'
)

# Detect drift
drift_results = detector.detect_drift(
    features,
    metrics=['error_rate', 'pattern_distribution', 'component_activity']
)
```

### 4. Visualization

Visualize results using the dashboard:

```python
from src.dashboard import visualization

# Initialize dashboard
dashboard = visualization.DriftDashboard()

# Display results
dashboard.plot_drift_metrics(drift_results)
dashboard.plot_temporal_patterns(features)
dashboard.plot_component_distribution(features)
```

## Common Use Cases

### 1. System Health Monitoring

Monitor system health through log pattern analysis:

```python
# Configure monitoring
monitor = system_monitor.HealthMonitor(
    check_interval='1H',
    alert_threshold=0.8
)

# Start monitoring
monitor.start_monitoring(
    log_sources=['HDFS', 'Apache'],
    metrics=['error_rate', 'response_time']
)
```

### 2. Error Pattern Analysis

Analyze error patterns and their evolution:

```python
# Initialize analyzer
analyzer = error_analyzer.ErrorPatternAnalyzer()

# Analyze patterns
patterns = analyzer.analyze_patterns(
    processed_data,
    pattern_window='24H',
    min_occurrence=5
)
```

### 3. Component Interaction Analysis

Study interactions between system components:

```python
# Initialize analyzer
component_analyzer = interaction_analyzer.ComponentAnalyzer()

# Analyze interactions
interactions = component_analyzer.analyze_interactions(
    processed_data,
    component_list=['namenode', 'datanode'],
    time_window='1D'
)
```

## Best Practices

1. **Data Preprocessing**
   - Clean and validate raw logs before processing
   - Handle missing or malformed entries
   - Standardize timestamp formats

2. **Feature Engineering**
   - Select appropriate time windows based on system behavior
   - Include domain-specific features
   - Normalize features when necessary

3. **Drift Detection**
   - Establish stable baseline periods
   - Set appropriate thresholds
   - Validate detection results

4. **Visualization**
   - Use appropriate visualizations for different metrics
   - Include temporal context
   - Highlight significant changes

## Configuration

### System Configuration

Edit `config/config.yaml`:

```yaml
preprocessing:
  time_format: '%Y-%m-%d %H:%M:%S'
  batch_size: 10000
  
feature_extraction:
  default_window: '1H'
  pattern_threshold: 0.1
  
drift_detection:
  baseline_period: '7D'
  detection_window: '1D'
  alert_threshold: 0.8
```

### Environment Variables

Required environment variables:

```bash
export LOG_LEVEL=INFO
export DATA_DIR=datasets/raw_drift_dataset
export PROCESSED_DIR=datasets/processed
```

## Troubleshooting

### Common Issues

1. **Data Processing Errors**
   ```python
   # Validate log format
   processor.validate_logs(input_path)
   
   # Check processing status
   processor.get_processing_status()
   ```

2. **Feature Extraction Issues**
   ```python
   # Verify feature completeness
   extractor.validate_features(features)
   
   # Check feature statistics
   extractor.get_feature_stats(features)
   ```

3. **Drift Detection Problems**
   ```python
   # Validate detection parameters
   detector.validate_parameters()
   
   # Check detection sensitivity
   detector.analyze_sensitivity(features)
   ```

## Advanced Usage

### Custom Feature Engineering

Create custom feature extractors:

```python
class CustomFeatureExtractor(BaseExtractor):
    def extract_features(self, data):
        # Custom feature extraction logic
        pass
```

### Custom Drift Detection

Implement custom drift detection algorithms:

```python
class CustomDriftDetector(BaseDriftDetector):
    def detect_drift(self, features):
        # Custom drift detection logic
        pass
```

## Next Steps

1. Explore advanced features in the documentation
2. Check example implementations in the source code
3. Contribute to the project development
4. Report issues and suggest improvements 