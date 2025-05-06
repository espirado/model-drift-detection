import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import List, Dict, Union, Optional, Tuple
from src.config.preprocessing_config import PreprocessingConfig
import os

class LogPreprocessor:
    """Class for preprocessing log data with configurable features and normalization."""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        """Initialize the log preprocessor with optional configuration.
        
        Args:
            config: PreprocessingConfig instance with preprocessing parameters
        """
        self.config = config or PreprocessingConfig()
        self.feature_stats: Dict[str, Dict[str, float]] = {}
    
    def parse_logs(self, logs: Union[List[str], pd.DataFrame], log_type: str = "default") -> pd.DataFrame:
        """Parse raw logs into a structured DataFrame.
        
        Args:
            logs: List of log strings or DataFrame with 'timestamp' and 'message' columns
            log_type: Type of log format ("default", "apache", "hdfs", "healthapp")
            
        Returns:
            DataFrame with parsed logs containing timestamp and message columns
        """
        if isinstance(logs, list):
            parsed_logs = []
            for log in logs:
                try:
                    timestamp = None
                    message = None
                    
                    if log_type == "apache":
                        # Apache log format: [Day Month DD HH:MM:SS YYYY]
                        timestamp_pattern = r'\[([\w\s:]+)\]'
                        match = re.search(timestamp_pattern, log)
                        if match:
                            try:
                                timestamp_str = match.group(1)
                                timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
                                # Get everything after the second bracket
                                message = log[log.find(']', log.find(']') + 1) + 1:].strip()
                            except ValueError as e:
                                print(f"Error parsing Apache timestamp: {e}")
                                continue
                    elif log_type == "hdfs":
                        # HDFS format: YYMMDD HHMMSS ThreadID Level Component: Message
                        parts = log.split(' ', 3)  # Split into timestamp parts and rest
                        if len(parts) >= 4:
                            try:
                                date_str = parts[0]
                                time_str = parts[1]
                                # Convert YYMMDD to YYYY-MM-DD
                                year = int('20' + date_str[:2])  # Assuming logs are from 2000s
                                month = int(date_str[2:4])
                                day = int(date_str[4:])
                                # Convert HHMMSS to HH:MM:SS
                                hour = int(time_str[:2])
                                minute = int(time_str[2:4])
                                second = int(time_str[4:])
                                
                                timestamp = datetime(year, month, day, hour, minute, second)
                                message = parts[3]  # Everything after ThreadID
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing HDFS timestamp: {e}")
                                continue
                    elif log_type == "healthapp":
                        # HealthApp format: YYYYMMDD-HH:MM:SS:MMM|Component|ID|Message
                        parts = log.split('|')
                        if len(parts) >= 4:
                            try:
                                timestamp_str = parts[0]  # YYYYMMDD-HH:MM:SS:MMM
                                # Convert to datetime, ignoring milliseconds
                                timestamp = datetime.strptime(timestamp_str.split(':')[0] + ':' + 
                                                           timestamp_str.split(':')[1] + ':' +
                                                           timestamp_str.split(':')[2], 
                                                           "%Y%m%d-%H:%M:%S")
                                # Combine component, ID, and message
                                message = f"{parts[1]}|{parts[2]}|{parts[3]}"
                            except (ValueError, IndexError) as e:
                                print(f"Error parsing HealthApp timestamp: {e}")
                                continue
                    else:
                        # Default format (YYYY-MM-DD HH:MM:SS)
                        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
                        match = re.search(timestamp_pattern, log)
                        if match:
                            timestamp = datetime.strptime(match.group(1), self.config.timestamp_format)
                            message = log[match.end():].strip()
                    
                    if timestamp and message:
                        parsed_logs.append({'timestamp': timestamp, 'message': message})
                except Exception as e:
                    print(f"Error parsing log: {log}\nError: {str(e)}")
                    continue
            
            return pd.DataFrame(parsed_logs)
        
        elif isinstance(logs, pd.DataFrame):
            if 'timestamp' not in logs.columns or 'message' not in logs.columns:
                raise ValueError("DataFrame must contain 'timestamp' and 'message' columns")
            
            # Convert timestamp to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(logs['timestamp']):
                if log_type == "apache":
                    logs['timestamp'] = pd.to_datetime(logs['timestamp'], format=self.config.apache_timestamp_format)
                else:
                    logs['timestamp'] = pd.to_datetime(logs['timestamp'], format=self.config.timestamp_format)
            
            return logs.copy()
        
        else:
            raise ValueError("logs must be either a list of strings or a DataFrame")
    
    def extract_basic_features(self, message: str) -> Dict[str, float]:
        """Extract basic features from a log message.
        
        Args:
            message: Log message string
            
        Returns:
            Dictionary of basic features and their values
        """
        features = {}
        
        if 'log_length' in self.config.basic_features:
            features['log_length'] = len(message)
        
        if 'word_count' in self.config.basic_features:
            features['word_count'] = len(message.split())
        
        if 'numeric_count' in self.config.basic_features:
            features['numeric_count'] = len(re.findall(r'\d+', message))
        
        if 'special_char_count' in self.config.basic_features:
            features['special_char_count'] = len(re.findall(r'[^a-zA-Z0-9\s]', message))
        
        if 'uppercase_count' in self.config.basic_features:
            features['uppercase_count'] = sum(1 for c in message if c.isupper())
        
        if 'lowercase_count' in self.config.basic_features:
            features['lowercase_count'] = sum(1 for c in message if c.islower())
        
        return features
    
    def extract_pattern_features(self, message: str) -> Dict[str, int]:
        """Extract pattern-based features from a log message.
        
        Args:
            message: Log message string
            
        Returns:
            Dictionary of pattern features and their counts
        """
        if not self.config.pattern_features:
            return {}
        
        features = {}
        for pattern_name, pattern in self.config.custom_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            features[f'pattern_{pattern_name}'] = len(matches)
        
        return features
    
    def create_time_windows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Group logs into time windows and aggregate features.
        
        Args:
            df: DataFrame with timestamp and extracted features
            
        Returns:
            DataFrame with aggregated features per time window
        """
        # Ensure timestamp is the index
        if df.index.name != 'timestamp':
            df = df.set_index('timestamp')
        
        # Create time windows
        windows = df.resample(self.config.window_size)
        
        # Filter windows based on log count limits
        valid_windows = []
        for _, window in windows:
            if len(window) >= self.config.min_logs_per_window:
                if self.config.max_logs_per_window:
                    window = window.head(self.config.max_logs_per_window)
                valid_windows.append(window)
        
        if not valid_windows:
            raise ValueError("No valid time windows found with the current configuration")
        
        # Combine all valid windows
        df_windows = pd.concat(valid_windows)
        
        # Aggregate numeric features
        numeric_cols = df_windows.select_dtypes(include=[np.number]).columns
        agg_dict = {col: ['mean', 'std', 'min', 'max'] for col in numeric_cols}
        
        return df_windows.groupby(pd.Grouper(freq=self.config.window_size)).agg(agg_dict)
    
    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize features using the specified method.
        
        Args:
            df: DataFrame with features to normalize
            
        Returns:
            DataFrame with normalized features
        """
        if self.config.normalization_method == "minmax":
            return self._minmax_normalize(df)
        elif self.config.normalization_method == "zscore":
            return self._zscore_normalize(df)
        else:
            raise ValueError(f"Unknown normalization method: {self.config.normalization_method}")
    
    def _minmax_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply min-max normalization to features."""
        normalized_df = df.copy()
        
        for column in df.columns:
            if column not in self.feature_stats:
                self.feature_stats[column] = {
                    'min': df[column].min(),
                    'max': df[column].max()
                }
            
            min_val = self.feature_stats[column]['min']
            max_val = self.feature_stats[column]['max']
            
            if max_val > min_val:
                normalized_df[column] = (df[column] - min_val) / (max_val - min_val)
            else:
                normalized_df[column] = 0  # Handle constant features
        
        return normalized_df
    
    def _zscore_normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply z-score normalization to features."""
        normalized_df = df.copy()
        
        for column in df.columns:
            if column not in self.feature_stats:
                self.feature_stats[column] = {
                    'mean': df[column].mean(),
                    'std': df[column].std()
                }
            
            mean_val = self.feature_stats[column]['mean']
            std_val = self.feature_stats[column]['std']
            
            if std_val > 0:
                normalized_df[column] = (df[column] - mean_val) / std_val
            else:
                normalized_df[column] = 0  # Handle constant features
        
        return normalized_df
    
    def process(self, logs: Union[List[str], pd.DataFrame], log_type: str = "default", output_path: Optional[str] = None) -> pd.DataFrame:
        """Process logs through the complete preprocessing pipeline.
        
        Args:
            logs: Raw logs as either a list of strings or a DataFrame
            log_type: Type of log format ("default", "apache", "hdfs")
            output_path: Optional path to save the processed data as CSV
            
        Returns:
            Processed DataFrame with normalized features in time windows
        """
        # Parse logs
        df = self.parse_logs(logs, log_type=log_type)
        
        # Extract features
        feature_dicts = []
        timestamps = []
        for idx, row in df.iterrows():
            features = {}
            features.update(self.extract_basic_features(row['message']))
            features.update(self.extract_pattern_features(row['message']))
            feature_dicts.append(features)
            timestamps.append(row['timestamp'])
        
        # Create feature DataFrame with timestamp
        feature_df = pd.DataFrame(feature_dicts)
        feature_df['timestamp'] = timestamps
        
        # Create time windows
        windowed_df = self.create_time_windows(feature_df)
        
        # Normalize features
        normalized_df = self.normalize_features(windowed_df)
        
        # Save processed data if output path is provided
        if output_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Save as CSV with timestamp as index
            normalized_df.to_csv(output_path)
            print(f"\nProcessed data saved to: {output_path}")
        
        return normalized_df
    
    def save_feature_stats(self, path: str):
        """Save feature statistics to a file."""
        pd.DataFrame(self.feature_stats).to_json(path)
    
    def load_feature_stats(self, path: str):
        """Load feature statistics from a file."""
        stats = pd.read_json(path)
        self.feature_stats = stats.to_dict() 