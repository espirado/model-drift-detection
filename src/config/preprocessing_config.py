from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re
from datetime import timedelta
import pandas as pd

@dataclass
class PreprocessingConfig:
    """Configuration class for log preprocessing parameters.
    
    This class defines all the parameters needed for the LogPreprocessor class
    to process log data, including time window settings, feature extraction options,
    and normalization methods.
    
    Attributes:
        timestamp_format (str): Format string for parsing timestamps (strftime format)
        apache_timestamp_format (str): Format string for parsing Apache timestamps
        window_size (str): Size of the time window (e.g., "1min", "2h", "1d")
        basic_features (List[str]): List of basic features to extract
        pattern_features (bool): Whether to extract pattern-based features
        custom_patterns (Dict[str, str]): Dictionary of custom regex patterns
        normalization_method (str): Method for feature normalization ("minmax" or "zscore")
        min_logs_per_window (int): Minimum number of logs required in a time window
        max_logs_per_window (Optional[int]): Maximum number of logs allowed in a time window
        window_stride (Optional[str]): Stride for sliding windows (default: same as window_size)
    """
    
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    apache_timestamp_format: str = "%a %b %d %H:%M:%S %Y"
    window_size: str = "5min"
    basic_features: List[str] = field(default_factory=lambda: [
        'log_length',
        'word_count',
        'numeric_count',
        'special_char_count',
        'uppercase_count',
        'lowercase_count'
    ])
    pattern_features: bool = True
    custom_patterns: Dict[str, str] = field(default_factory=lambda: {
        'error': r'error|exception|fail|failed|failure',
        'warning': r'warn|warning|high|critical',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'metrics': r'\d+%|\d+(?:\.\d+)?(?:GB|MB|KB|ms|sec)',
        'user': r'user\s*\w+|username|userid'
    })
    normalization_method: str = "minmax"
    min_logs_per_window: int = 1
    max_logs_per_window: Optional[int] = None
    window_stride: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration parameters after initialization."""
        self._validate_window_size()
        self._validate_normalization_method()
        self._validate_patterns()
        self._validate_features()
        self._validate_window_params()
    
    def _validate_window_size(self):
        """Validate the window size format."""
        try:
            self._parse_time_str(self.window_size)
        except ValueError as e:
            raise ValueError(f"Invalid window_size format: {self.window_size}. " 
                           "Expected format: number + unit (e.g., '5min', '2h', '1d')")
    
    def _validate_normalization_method(self):
        """Validate the normalization method."""
        valid_methods = ["minmax", "zscore"]
        if self.normalization_method not in valid_methods:
            raise ValueError(f"Invalid normalization_method: {self.normalization_method}. "
                           f"Must be one of {valid_methods}")
    
    def _validate_patterns(self):
        """Validate custom regex patterns."""
        if not isinstance(self.custom_patterns, dict):
            raise ValueError("custom_patterns must be a dictionary")
        
        for name, pattern in self.custom_patterns.items():
            try:
                re.compile(pattern)
            except re.error:
                raise ValueError(f"Invalid regex pattern for {name}: {pattern}")
    
    def _validate_features(self):
        """Validate basic features list."""
        valid_features = {
            'log_length',
            'word_count',
            'numeric_count',
            'special_char_count',
            'uppercase_count',
            'lowercase_count'
        }
        
        invalid_features = set(self.basic_features) - valid_features
        if invalid_features:
            raise ValueError(f"Invalid basic features: {invalid_features}. "
                           f"Valid features are: {valid_features}")
    
    def _validate_window_params(self):
        """Validate window-related parameters."""
        if self.min_logs_per_window < 1:
            raise ValueError("min_logs_per_window must be at least 1")
        
        if (self.max_logs_per_window is not None and 
            self.max_logs_per_window < self.min_logs_per_window):
            raise ValueError("max_logs_per_window must be greater than or equal to min_logs_per_window")
        
        if self.window_stride is not None:
            try:
                self._parse_time_str(self.window_stride)
            except ValueError:
                raise ValueError(f"Invalid window_stride format: {self.window_stride}")
    
    @staticmethod
    def _parse_time_str(time_str: str) -> timedelta:
        """Parse a time string into a timedelta object.
        
        Args:
            time_str: String in format "number + unit" (e.g., "5min", "2h", "1d")
            
        Returns:
            timedelta object representing the time duration
        """
        if not isinstance(time_str, str):
            raise ValueError("Time string must be a string")
        
        # Extract number and unit
        match = re.match(r'(\d+)([a-zA-Z]+)', time_str)
        if not match:
            raise ValueError(f"Invalid time format: {time_str}")
        
        value, unit = match.groups()
        value = int(value)
        
        # Convert to timedelta
        unit_map = {
            's': 'seconds',
            'sec': 'seconds',
            'm': 'minutes',
            'min': 'minutes',
            'h': 'hours',
            'hr': 'hours',
            'd': 'days',
            'day': 'days'
        }
        
        if unit.lower() not in unit_map:
            raise ValueError(f"Invalid time unit: {unit}")
        
        return pd.Timedelta(**{unit_map[unit.lower()]: value})
    
    def get_window_timedelta(self) -> pd.Timedelta:
        """Get the window size as a pandas Timedelta object."""
        return self._parse_time_str(self.window_size)
    
    def get_stride_timedelta(self) -> pd.Timedelta:
        """Get the window stride as a pandas Timedelta object."""
        if self.window_stride is None:
            return self.get_window_timedelta()
        return self._parse_time_str(self.window_stride)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary format."""
        return {
            'timestamp_format': self.timestamp_format,
            'apache_timestamp_format': self.apache_timestamp_format,
            'window_size': self.window_size,
            'basic_features': self.basic_features,
            'pattern_features': self.pattern_features,
            'custom_patterns': self.custom_patterns,
            'normalization_method': self.normalization_method,
            'min_logs_per_window': self.min_logs_per_window,
            'max_logs_per_window': self.max_logs_per_window,
            'window_stride': self.window_stride
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'PreprocessingConfig':
        """Create configuration from dictionary format."""
        return cls(**config_dict) 