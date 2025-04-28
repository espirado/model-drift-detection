# Project Structure

This document outlines the organization of the System Reliability Drift Detection project.

## Directory Structure

```
model-drift-detection/
├── data/                  # Log datasets from Loghub
│   ├── raw/               # Raw log files
│   ├── processed/         # Processed and parsed logs
│   └── README.md          # Dataset documentation
├── src/
│   ├── ingestion/         # Log ingestion from Kafka
│   │   ├── kafka_producer.py
│   │   └── log_loader.py
│   ├── parsing/           # Log parsing and feature extraction
│   │   ├── log_parser.py
│   │   ├── feature_extractor.py
│   │   └── pattern_analyzer.py
│   ├── detection/         # Drift detection algorithms
│   │   ├── distribution_drift.py
│   │   ├── error_rate_drift.py
│   │   ├── pattern_drift.py
│   │   └── anomaly_detector.py
│   ├── visualization/     # Dashboards and alerts
│   │   ├── dashboard.py
│   │   ├── alert_manager.py
│   │   └── metrics_visualizer.py
│   └── utils/             # Utility functions
│       ├── config.py
│       ├── logging.py
│       └── helpers.py
├── config/                # Configuration files
│   ├── kafka_config.yaml
│   ├── detection_config.yaml
│   └── visualization_config.yaml
├── docs/                  # Documentation
│   ├── setup.md
│   ├── usage.md
│   └── project_structure.md
├── tests/                 # Test files
│   ├── test_parsing.py
│   ├── test_detection.py
│   └── test_visualization.py
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

## Component Descriptions

### Data Directory
- **raw/**: Contains the original log files from Loghub
- **processed/**: Contains parsed and processed log data ready for analysis
- **README.md**: Documentation of available datasets and their characteristics

### Source Code (src/)

#### Ingestion Module
- **kafka_producer.py**: Handles streaming logs to Kafka
- **log_loader.py**: Loads logs from files or other sources

#### Parsing Module
- **log_parser.py**: Parses raw logs into structured formats
- **feature_extractor.py**: Extracts relevant features from parsed logs
- **pattern_analyzer.py**: Analyzes log patterns for drift detection

#### Detection Module
- **distribution_drift.py**: Implements distribution-based drift detection
- **error_rate_drift.py**: Monitors for changes in error rates
- **pattern_drift.py**: Detects shifts in log message patterns
- **anomaly_detector.py**: Identifies anomalies in log streams

#### Visualization Module
- **dashboard.py**: Creates real-time monitoring dashboards
- **alert_manager.py**: Manages and sends alerts for detected drift
- **metrics_visualizer.py**: Visualizes reliability metrics

#### Utilities
- **config.py**: Configuration management
- **logging.py**: Logging utilities
- **helpers.py**: Helper functions used across modules

### Configuration (config/)
- **kafka_config.yaml**: Kafka connection and topic settings
- **detection_config.yaml**: Drift detection algorithm parameters
- **visualization_config.yaml**: Dashboard and visualization settings

### Documentation (docs/)
- **setup.md**: Installation and setup instructions
- **usage.md**: Usage examples and API documentation
- **project_structure.md**: This document

### Tests (tests/)
- Unit and integration tests for each module

## Key Files

- **requirements.txt**: Lists all Python dependencies
- **README.md**: Project overview and getting started guide 