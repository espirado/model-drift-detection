import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile

from ...src.preprocessing.log_preprocessor import LogPreprocessor
from ...src.config.preprocessing_config import PreprocessingConfig

@pytest.fixture
def sample_logs():
    """Create sample log messages for testing."""
    return [
        "2024-03-15 10:00:00 INFO User login successful for user123",
        "2024-03-15 10:01:00 ERROR Failed to connect to database [retry=3]",
        "2024-03-15 10:02:00 WARNING High CPU usage detected: 95%",
        "2024-03-15 10:03:00 INFO Memory usage: 8.5GB of 16GB used",
        "2024-03-15 10:04:00 DEBUG Processing batch job #12345"
    ]

@pytest.fixture
def sample_df(sample_logs):
    """Create a sample DataFrame with parsed logs."""
    data = []
    for log in sample_logs:
        timestamp = datetime.strptime(log[:19], "%Y-%m-%d %H:%M:%S")
        message = log[20:]
        data.append({"timestamp": timestamp, "message": message})
    return pd.DataFrame(data)

@pytest.fixture
def config():
    """Create a test configuration."""
    return PreprocessingConfig(
        timestamp_format="%Y-%m-%d %H:%M:%S",
        window_size="2min",
        basic_features=['log_length', 'word_count', 'numeric_count'],
        pattern_features=True,
        custom_patterns={
            'error': r'error|failed|failure',
            'warning': r'warning|high|critical',
            'metrics': r'\d+%|\d+GB'
        },
        normalization_method="minmax",
        min_logs_per_window=1
    )

@pytest.fixture
def preprocessor(config):
    """Create a LogPreprocessor instance with test configuration."""
    return LogPreprocessor(config)

def test_initialization():
    """Test LogPreprocessor initialization."""
    # Test with default config
    preprocessor = LogPreprocessor()
    assert preprocessor.config is not None
    assert isinstance(preprocessor.config, PreprocessingConfig)
    
    # Test with custom config
    custom_config = PreprocessingConfig(window_size="10min")
    preprocessor = LogPreprocessor(custom_config)
    assert preprocessor.config.window_size == "10min"

def test_parse_logs_from_strings(preprocessor, sample_logs):
    """Test parsing logs from list of strings."""
    df = preprocessor.parse_logs(sample_logs)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(sample_logs)
    assert all(col in df.columns for col in ['timestamp', 'message'])
    assert isinstance(df['timestamp'].iloc[0], pd.Timestamp)

def test_parse_logs_from_dataframe(preprocessor, sample_df):
    """Test parsing logs from DataFrame."""
    df = preprocessor.parse_logs(sample_df)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == len(sample_df)
    assert all(col in df.columns for col in ['timestamp', 'message'])

def test_parse_logs_invalid_input(preprocessor):
    """Test parsing logs with invalid input."""
    with pytest.raises(ValueError):
        preprocessor.parse_logs(123)  # Invalid type
    
    with pytest.raises(ValueError):
        preprocessor.parse_logs(pd.DataFrame({'col1': [1, 2, 3]}))  # Missing required columns

def test_extract_basic_features(preprocessor):
    """Test basic feature extraction."""
    message = "ERROR: Database connection failed after 3 retries!"
    features = preprocessor.extract_basic_features(message)
    
    assert 'log_length' in features
    assert features['log_length'] == len(message)
    
    assert 'word_count' in features
    assert features['word_count'] == 7
    
    assert 'numeric_count' in features
    assert features['numeric_count'] == 1

def test_extract_pattern_features(preprocessor):
    """Test pattern-based feature extraction."""
    message = "ERROR: High CPU usage at 95% detected"
    features = preprocessor.extract_pattern_features(message)
    
    assert 'pattern_error' in features
    assert features['pattern_error'] == 1
    
    assert 'pattern_warning' in features
    assert features['pattern_warning'] == 1
    
    assert 'pattern_metrics' in features
    assert features['pattern_metrics'] == 1

def test_create_time_windows(preprocessor, sample_df):
    """Test time window creation and aggregation."""
    # Extract features first
    feature_dicts = []
    for message in sample_df['message']:
        features = {}
        features.update(preprocessor.extract_basic_features(message))
        features.update(preprocessor.extract_pattern_features(message))
        feature_dicts.append(features)
    
    feature_df = pd.DataFrame(feature_dicts, index=sample_df['timestamp'])
    
    # Create time windows
    windowed_df = preprocessor.create_time_windows(feature_df)
    
    assert isinstance(windowed_df, pd.DataFrame)
    assert len(windowed_df) > 0
    # Check if we have mean, std, min, max for each feature
    for col in feature_df.columns:
        assert any(col in multi_col[0] for multi_col in windowed_df.columns)

def test_normalize_features_minmax(preprocessor):
    """Test min-max normalization."""
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    
    normalized = preprocessor._minmax_normalize(df)
    
    assert normalized['feature1'].min() >= 0
    assert normalized['feature1'].max() <= 1
    assert normalized['feature2'].min() >= 0
    assert normalized['feature2'].max() <= 1

def test_normalize_features_zscore(preprocessor):
    """Test z-score normalization."""
    preprocessor.config.normalization_method = "zscore"
    data = {
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    
    normalized = preprocessor._zscore_normalize(df)
    
    assert abs(normalized['feature1'].mean()) < 1e-10
    assert abs(normalized['feature1'].std() - 1.0) < 1e-10
    assert abs(normalized['feature2'].mean()) < 1e-10
    assert abs(normalized['feature2'].std() - 1.0) < 1e-10

def test_normalize_features_constant(preprocessor):
    """Test normalization with constant features."""
    data = {
        'constant': [5, 5, 5, 5, 5],
        'variable': [1, 2, 3, 4, 5]
    }
    df = pd.DataFrame(data)
    
    normalized = preprocessor.normalize_features(df)
    
    assert all(normalized['constant'] == 0)  # Constant features should be set to 0
    assert normalized['variable'].std() > 0  # Variable features should be normalized

def test_process_end_to_end(preprocessor, sample_logs):
    """Test complete preprocessing pipeline."""
    result = preprocessor.process(sample_logs)
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    # Check if we have aggregated features
    assert all('mean' in col[1] for col in result.columns)
    assert all('std' in col[1] for col in result.columns)

def test_feature_stats_persistence(preprocessor, sample_logs, tmp_path):
    """Test saving and loading feature statistics."""
    # Process some data to generate statistics
    preprocessor.process(sample_logs)
    
    # Save statistics
    stats_file = tmp_path / "feature_stats.json"
    preprocessor.save_feature_stats(str(stats_file))
    
    # Create new preprocessor and load statistics
    new_preprocessor = LogPreprocessor(preprocessor.config)
    new_preprocessor.load_feature_stats(str(stats_file))
    
    # Compare statistics
    assert preprocessor.feature_stats == new_preprocessor.feature_stats

def test_error_handling(preprocessor):
    """Test error handling in various scenarios."""
    # Test invalid window size
    with pytest.raises(ValueError):
        invalid_config = PreprocessingConfig(window_size="invalid")
        LogPreprocessor(invalid_config)
    
    # Test empty log list
    with pytest.raises(ValueError):
        preprocessor.process([])
    
    # Test invalid normalization method
    with pytest.raises(ValueError):
        invalid_config = PreprocessingConfig(normalization_method="invalid")
        LogPreprocessor(invalid_config)

def test_custom_pattern_validation(preprocessor):
    """Test custom pattern validation."""
    # Test invalid regex pattern
    with pytest.raises(ValueError):
        invalid_config = PreprocessingConfig(
            custom_patterns={'invalid': '['}  # Invalid regex
        )
        LogPreprocessor(invalid_config)

def test_window_size_validation():
    """Test window size validation."""
    # Valid window sizes
    valid_sizes = ["1min", "2h", "1d", "30s"]
    for size in valid_sizes:
        config = PreprocessingConfig(window_size=size)
        assert config.window_size == size
    
    # Invalid window sizes
    invalid_sizes = ["1x", "min", "hour", ""]
    for size in invalid_sizes:
        with pytest.raises(ValueError):
            PreprocessingConfig(window_size=size) 