"""
Log Analysis Module for Model Drift Detection Project

This module provides comprehensive analysis capabilities for various types of system logs,
including HDFS, Apache, HealthApp, BGL, HPC, Linux, and Mac logs. It is designed to help
identify patterns, anomalies, and potential drift in system behavior across different
log sources.

Key Features:
- Multi-format log parsing
- Structure analysis
- Field completeness checking
- Statistical analysis
- Visualization of log characteristics

Usage:
    analyzer = LogAnalyzer()
    analyzer.read_logs()
    analyzer.parse_logs()
    analyzer.analyze_all()

Author: DS-600 Project Team
Date: 2024
"""

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from pathlib import Path

# Set plotting style for consistent visualizations
plt.style.use('seaborn')
sns.set_palette('husl')

class LogAnalyzer:
    """
    A class for analyzing various types of system logs.
    
    This class provides methods for reading, parsing, and analyzing different types of log files.
    It supports multiple log formats and provides various analysis capabilities to understand
    log patterns and characteristics.
    
    Attributes:
        base_path (Path): Base directory containing log files
        datasets (dict): Mapping of dataset names to their file paths
        logs (dict): Raw log entries for each dataset
        parsed_logs (dict): Parsed and structured log data
    """

    def __init__(self, base_path='../datasets/raw_drift_dataset'):
        """
        Initialize the LogAnalyzer with paths to different log files.
        
        Args:
            base_path (str): Path to the directory containing log datasets
        """
        self.base_path = Path(base_path)
        # Define paths for all supported log types
        self.datasets = {
            'HDFS': self.base_path / 'HDFS' / 'hdfs.log',      # Hadoop Distributed File System logs
            'Apache': self.base_path / 'Apache' / 'Apache.log', # Web server logs
            'HealthApp': self.base_path / 'HealthApp' / 'HealthApp.log', # Healthcare application logs
            'BGL': self.base_path / 'BGL' / 'BGL.log',         # Blue Gene/L supercomputer logs
            'HPC': self.base_path / 'HPC' / 'HPC.log',         # High Performance Computing logs
            'Linux': self.base_path / 'Linux' / 'Linux.log',   # Linux system logs
            'Mac': self.base_path / 'Mac' / 'Mac.log'          # macOS system logs
        }
        self.logs = {}          # Store raw log entries
        self.parsed_logs = {}   # Store structured log data

    def read_logs(self):
        """
        Read all log files from the specified paths.
        
        This method attempts to read each log file, handling potential errors such as
        missing files or encoding issues. It stores non-empty log lines for each dataset.
        
        Raises:
            FileNotFoundError: If a log file is not found
            Exception: For other reading errors (encoding, permissions, etc.)
        """
        for name, path in self.datasets.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.logs[name] = [line.strip() for line in f.readlines() if line.strip()]
                print(f"{name} Logs: {len(self.logs[name])} entries")
            except FileNotFoundError:
                print(f"Warning: {name} log file not found at {path}")
            except Exception as e:
                print(f"Error reading {name} logs: {str(e)}")

    def parse_logs(self):
        """
        Parse raw log entries into structured data.
        
        This method applies format-specific parsers to each dataset, converting
        raw log strings into structured dictionaries with standardized fields.
        Each log type has its own parser that extracts relevant information.
        """
        parsers = {
            'HDFS': self._parse_hdfs,         # Parse HDFS log format
            'Apache': self._parse_apache,      # Parse Apache web server logs
            'HealthApp': self._parse_health,   # Parse HealthApp application logs
            'BGL': self._parse_bgl,           # Parse Blue Gene/L logs
            'HPC': self._parse_hpc,           # Parse HPC cluster logs
            'Linux': self._parse_linux,        # Parse Linux system logs
            'Mac': self._parse_mac            # Parse macOS system logs
        }
        
        for name, logs in self.logs.items():
            if name in parsers:
                self.parsed_logs[name] = [parsers[name](log) for log in logs]
            else:
                print(f"Warning: No parser defined for {name}")

    def _parse_hdfs(self, log):
        """
        Parse HDFS log format.
        
        Format: [Date Time] [Severity] [Component] [Message]
        Example: 081109 203515 INFO dfs.FSNamesystem FSNamesystem.audit: allowed=true
        
        Args:
            log (str): Raw log entry
            
        Returns:
            dict: Parsed log entry with standardized fields
        """
        pattern = r'(\d{6} \d{6}) (\w+) ([\w\.]+) (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, severity, component, message = match.groups()
            return {
                'timestamp': timestamp,
                'severity': severity,
                'component': component,
                'message': message
            }
        return None

    def _parse_apache(self, log):
        """Parse Apache log format."""
        pattern = r'(\S+) \S+ \S+ \[(.*?)\] "(.*?)" (\d+) (\d+)'
        match = re.match(pattern, log)
        if match:
            ip, timestamp, request, status, size = match.groups()
            return {
                'ip': ip,
                'timestamp': timestamp,
                'request': request,
                'status': status,
                'size': size
            }
        return None

    def _parse_health(self, log):
        """Parse HealthApp log format."""
        pattern = r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, component, severity, user_id, message = match.groups()
            return {
                'timestamp': timestamp,
                'component': component,
                'severity': severity,
                'user_id': user_id,
                'message': message
            }
        return None

    def _parse_bgl(self, log):
        """Parse BGL log format."""
        pattern = r'(\d{6} \d{6}) (\S+) (\w+) (\w+) (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, location, severity, component, message = match.groups()
            return {
                'timestamp': timestamp,
                'location': location,
                'severity': severity,
                'component': component,
                'message': message
            }
        return None

    def _parse_hpc(self, log):
        """Parse HPC log format."""
        pattern = r'(\d{6} \d{6}) (\w+) (\w+) (\w+) (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, node_id, job_id, severity, message = match.groups()
            return {
                'timestamp': timestamp,
                'node_id': node_id,
                'job_id': job_id,
                'severity': severity,
                'message': message
            }
        return None

    def _parse_linux(self, log):
        """Parse Linux log format."""
        pattern = r'(\w+ \d+ \d+:\d+:\d+) (\S+) (\w+)\[(\d+)\]: (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, hostname, process, pid, message = match.groups()
            return {
                'timestamp': timestamp,
                'hostname': hostname,
                'process': process,
                'pid': pid,
                'message': message
            }
        return None

    def _parse_mac(self, log):
        """Parse Mac log format."""
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) (\w+) (\w+): (.+)'
        match = re.match(pattern, log)
        if match:
            timestamp, sender, type_, category, message = match.groups()
            return {
                'timestamp': timestamp,
                'sender': sender,
                'type': type_,
                'category': category,
                'message': message
            }
        return None

    def analyze_structure(self, dataset_name):
        """
        Analyze the structure and characteristics of a specific dataset.
        
        This method performs several analyses:
        1. Basic statistics (min, max, mean, std) of log entry lengths
        2. Field completeness analysis for parsed logs
        3. Visualization of log length distribution
        
        Args:
            dataset_name (str): Name of the dataset to analyze
        """
        if dataset_name not in self.logs:
            print(f"Dataset {dataset_name} not found")
            return

        logs = self.logs[dataset_name]
        parsed = self.parsed_logs.get(dataset_name, [])
        
        print(f"\n{dataset_name} Log Structure Analysis:")
        
        # Calculate and display basic statistics
        lengths = [len(log) for log in logs]
        print(f"Length statistics:")
        print(f"- Min: {min(lengths)}")
        print(f"- Max: {max(lengths)}")
        print(f"- Mean: {np.mean(lengths):.2f}")
        print(f"- Std: {np.std(lengths):.2f}")
        
        # Analyze field completeness
        if parsed:
            fields = parsed[0].keys()
            for field in fields:
                complete = sum(1 for p in parsed if p and p.get(field)) / len(parsed) * 100
                print(f"{field} completeness: {complete:.2f}%")

        # Create visualization
        plt.figure(figsize=(10, 5))
        plt.hist(lengths, bins=50)
        plt.title(f"{dataset_name} Log Length Distribution")
        plt.xlabel("Log Length")
        plt.ylabel("Frequency")
        plt.show()

    def analyze_all(self):
        """
        Perform analysis on all available datasets.
        
        This method iterates through all loaded datasets and performs
        structure analysis on each one, providing a comprehensive view
        of the characteristics across different log types.
        """
        for dataset_name in self.logs.keys():
            self.analyze_structure(dataset_name)

def main():
    """
    Main execution function.
    
    This function demonstrates the typical workflow for using the LogAnalyzer:
    1. Create an analyzer instance
    2. Read all log files
    3. Parse logs into structured format
    4. Perform analysis on all datasets
    """
    analyzer = LogAnalyzer()
    analyzer.read_logs()
    analyzer.parse_logs()
    analyzer.analyze_all()

if __name__ == "__main__":
    main() 