# User Guide

## Getting Started

This guide provides instructions for using the Model Drift Detection system to analyze system logs and detect drift patterns.

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   pip install -r requirements.txt
   ```

2. **Prepare Data**
   - Place log files in appropriate directories under `datasets/raw_drift_dataset/`
   - Ensure correct file formats and permissions

3. **Run Analysis**
   - Use provided scripts in `src/` directory
   - Follow analysis pipeline steps
   - Check results in output directories

## Usage Examples

### 1. Process Log Files
```python
from src.preprocessing import log_processor

# Initialize processor
processor = log_processor.LogProcessor()

# Process logs
processed_data = processor.process_logs(
    log_type="HDFS",
    input_path="datasets/raw_drift_dataset/HDFS",
    output_path="datasets/processed/hdfs_processed.csv"
)
```

### 2. Analyze Patterns
```python
from src.features import pattern_analyzer

# Initialize analyzer
analyzer = pattern_analyzer.PatternAnalyzer()

# Analyze patterns
patterns = analyzer.analyze_patterns(
    processed_data,
    window_size='1H'
)
```

### 3. Detect Drift
```python
from src.detection import drift_detector

# Initialize detector
detector = drift_detector.DriftDetector()

# Detect drift
results = detector.detect_drift(
    current_data=patterns,
    baseline_data=baseline_patterns
)
```

## Common Tasks

1. **Data Preprocessing**
   - Log parsing
   - Feature extraction
   - Data validation

2. **Pattern Analysis**
   - Temporal analysis
   - Component analysis
   - Error analysis

3. **Drift Detection**
   - Distribution analysis
   - Pattern evolution
   - Alert generation

## Troubleshooting

1. **Data Issues**
   - Check file permissions
   - Verify file formats
   - Validate data structure

2. **Processing Errors**
   - Check log format
   - Verify timestamps
   - Validate features

3. **Detection Issues**
   - Check thresholds
   - Verify baseline
   - Validate metrics

## Support

For additional help:
1. Check documentation in `docs/`
2. Review example code
3. Contact support team
