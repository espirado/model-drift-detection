from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import timedelta

@dataclass
class PreprocessingConfig:
    # Time-related settings
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    window_size: timedelta = timedelta(minutes=5)
    
    # Feature extraction settings
    basic_features: List[str] = None
    pattern_features: bool = True
    custom_patterns: Optional[Dict[str, str]] = None
    
    # Normalization settings
    normalization_method: str = "minmax"  # Options: minmax, zscore
    feature_scaling_range: tuple = (0, 1)
    
    # Log parsing settings
    log_pattern_threshold: float = 0.1  # Minimum frequency for pattern recognition
    max_pattern_length: int = 100
    
    def __post_init__(self):
        if self.basic_features is None:
            self.basic_features = [
                "log_length",
                "word_count",
                "special_char_count",
                "numeric_count"
            ]
        
        if self.custom_patterns is None:
            self.custom_patterns = {
                "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
                "error_code": r"Error \d+",
                "port_number": r"port \d+",
                "url": r"https?://\S+",
            }

# Default configuration instance
default_config = PreprocessingConfig() 