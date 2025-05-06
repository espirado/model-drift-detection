import pytest
from datetime import timedelta
import pandas as pd
from src.config.preprocessing_config import PreprocessingConfig

def test_default_initialization():
    """Test initialization with default values."""
    config = PreprocessingConfig()
    assert config.timestamp_format == "%Y-%m-%d %H:%M:%S"
    assert config.window_size == "5min"
    assert "log_length" in config.basic_features
    assert config.pattern_features is True
    assert "error" in config.custom_patterns
    assert config.normalization_method == "minmax"
    assert config.min_logs_per_window == 1
    assert config.max_logs_per_window is None
    assert config.window_stride is None

def test_custom_initialization():
    """Test initialization with custom values."""
    custom_config = PreprocessingConfig(
        timestamp_format="%Y-%m-%d %H:%M",
        window_size="1h",
        basic_features=["log_length", "word_count"],
        pattern_features=False,
        custom_patterns={"test": r"\d+"},
        normalization_method="zscore",
        min_logs_per_window=5,
        max_logs_per_window=100,
        window_stride="30min"
    )
    assert custom_config.timestamp_format == "%Y-%m-%d %H:%M"
    assert custom_config.window_size == "1h"
    assert custom_config.basic_features == ["log_length", "word_count"]
    assert custom_config.pattern_features is False
    assert custom_config.custom_patterns == {"test": r"\d+"}
    assert custom_config.normalization_method == "zscore"
    assert custom_config.min_logs_per_window == 5
    assert custom_config.max_logs_per_window == 100
    assert custom_config.window_stride == "30min"

@pytest.mark.parametrize("window_size,expected", [
    ("5min", pd.Timedelta(minutes=5)),
    ("1h", pd.Timedelta(hours=1)),
    ("24h", pd.Timedelta(hours=24)),
    ("1d", pd.Timedelta(days=1)),
    ("60s", pd.Timedelta(seconds=60)),
])
def test_valid_window_sizes(window_size, expected):
    """Test various valid window size formats."""
    config = PreprocessingConfig(window_size=window_size)
    assert config.get_window_timedelta() == expected

@pytest.mark.parametrize("invalid_size", [
    "invalid",
    "5",
    "min5",
    "-5min",
    "5.5min",
    "5mins",
    "5x",
])
def test_invalid_window_sizes(invalid_size):
    """Test invalid window size formats."""
    with pytest.raises(ValueError):
        PreprocessingConfig(window_size=invalid_size)

def test_window_stride():
    """Test window stride functionality."""
    # Test default stride (None)
    config = PreprocessingConfig(window_size="5min")
    assert config.get_stride_timedelta() == pd.Timedelta(minutes=5)
    
    # Test custom stride
    config = PreprocessingConfig(window_size="1h", window_stride="30min")
    assert config.get_stride_timedelta() == pd.Timedelta(minutes=30)
    
    # Test invalid stride
    with pytest.raises(ValueError):
        PreprocessingConfig(window_size="1h", window_stride="invalid")

@pytest.mark.parametrize("method", ["minmax", "zscore"])
def test_valid_normalization_methods(method):
    """Test valid normalization methods."""
    config = PreprocessingConfig(normalization_method=method)
    assert config.normalization_method == method

def test_invalid_normalization_method():
    """Test invalid normalization method."""
    with pytest.raises(ValueError):
        PreprocessingConfig(normalization_method="invalid")

def test_window_limits_validation():
    """Test window size limits validation."""
    # Valid cases
    PreprocessingConfig(min_logs_per_window=1, max_logs_per_window=10)
    PreprocessingConfig(min_logs_per_window=5, max_logs_per_window=5)
    PreprocessingConfig(min_logs_per_window=1, max_logs_per_window=None)
    
    # Invalid cases
    with pytest.raises(ValueError):
        PreprocessingConfig(min_logs_per_window=0)
    
    with pytest.raises(ValueError):
        PreprocessingConfig(min_logs_per_window=10, max_logs_per_window=5)

def test_basic_features_validation():
    """Test basic features validation."""
    # Valid features
    valid_features = [
        'log_length',
        'word_count',
        'numeric_count',
        'special_char_count',
        'uppercase_count',
        'lowercase_count'
    ]
    config = PreprocessingConfig(basic_features=valid_features)
    assert config.basic_features == valid_features
    
    # Invalid features
    with pytest.raises(ValueError):
        PreprocessingConfig(basic_features=['invalid_feature'])

def test_custom_patterns_validation():
    """Test custom patterns validation."""
    # Valid patterns
    valid_patterns = {
        'test1': r'\d+',
        'test2': r'[a-z]+',
        'test3': r'\b\w+\b'
    }
    config = PreprocessingConfig(custom_patterns=valid_patterns)
    assert config.custom_patterns == valid_patterns
    
    # Invalid patterns
    with pytest.raises(ValueError):
        PreprocessingConfig(custom_patterns={'test': r'['})  # Invalid regex

def test_to_dict():
    """Test conversion to dictionary."""
    config = PreprocessingConfig(
        window_size="1h",
        basic_features=["log_length"],
        normalization_method="zscore"
    )
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['window_size'] == "1h"
    assert config_dict['basic_features'] == ["log_length"]
    assert config_dict['normalization_method'] == "zscore"

def test_from_dict():
    """Test creation from dictionary."""
    config_dict = {
        'timestamp_format': "%Y-%m-%d %H:%M",
        'window_size': "1h",
        'basic_features': ["log_length"],
        'pattern_features': False,
        'custom_patterns': {"test": r"\d+"},
        'normalization_method': "zscore",
        'min_logs_per_window': 5,
        'max_logs_per_window': 100,
        'window_stride': "30min"
    }
    
    config = PreprocessingConfig.from_dict(config_dict)
    assert config.timestamp_format == config_dict['timestamp_format']
    assert config.window_size == config_dict['window_size']
    assert config.basic_features == config_dict['basic_features']
    assert config.pattern_features == config_dict['pattern_features']
    assert config.custom_patterns == config_dict['custom_patterns']
    assert config.normalization_method == config_dict['normalization_method']
    assert config.min_logs_per_window == config_dict['min_logs_per_window']
    assert config.max_logs_per_window == config_dict['max_logs_per_window']
    assert config.window_stride == config_dict['window_stride'] 