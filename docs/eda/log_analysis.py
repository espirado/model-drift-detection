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
from collections import defaultdict
import os
from typing import Dict, List, Tuple, Optional
import chardet

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

    def __init__(self, base_path: str):
        """Initialize LogAnalyzer with base path to log files."""
        self.base_path = base_path
        self.log_paths = {
            'HDFS': os.path.join(base_path, 'HDFS/hdfs.log'),
            'Apache': os.path.join(base_path, 'Apache/apache.log'),
            'HealthApp': os.path.join(base_path, 'HealthApp/HealthApp.log'),
            'BGL': os.path.join(base_path, 'BGL/BGL.log'),
            'HPC': os.path.join(base_path, 'HPC/HPC.log'),
            'Linux': os.path.join(base_path, 'Linux/Linux.log'),
            'Mac': os.path.join(base_path, 'Mac/Mac.log')
        }
        
    def detect_encoding(self, file_path: str) -> str:
        """Detect the encoding of a file."""
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Read first 10000 bytes
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    
    def read_log_sample(self, log_type: str, sample_size: int = 1000) -> List[str]:
        """Read a sample of lines from a log file with proper encoding handling."""
        try:
            file_path = self.log_paths[log_type]
            encoding = self.detect_encoding(file_path)
            
            lines = []
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                for i, line in enumerate(f):
                    if i >= sample_size:
                        break
                    if line.strip():
                        lines.append(line.strip())
            return lines
        except Exception as e:
            print(f"Error reading {log_type} log: {str(e)}")
            return []

    def analyze_log_structure(self, log_type: str) -> Dict:
        """Analyze basic structure of log entries."""
        lines = self.read_log_sample(log_type)
        if not lines:
            return {}
        
        analysis = {
            'total_lines': len(lines),
            'avg_length': np.mean([len(line) for line in lines]),
            'min_length': min(len(line) for line in lines),
            'max_length': max(len(line) for line in lines),
            'sample_entries': lines[:5]
        }
        
        # Detect common patterns
        timestamp_patterns = [
            r'\d{6}\s+\d{6}',  # HDFS format: YYMMDD HHMMSS
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # ISO format
            r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'  # Syslog format
        ]
        
        for line in lines[:100]:  # Check first 100 lines
            for pattern in timestamp_patterns:
                if re.search(pattern, line):
                    analysis['timestamp_format'] = pattern
                    break
            if 'timestamp_format' in analysis:
                break
        
        # Detect log levels
        log_levels = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'CRITICAL']
        level_counts = defaultdict(int)
        for line in lines:
            for level in log_levels:
                if f" {level} " in line or f"[{level}]" in line:
                    level_counts[level] += 1
        
        analysis['log_levels'] = dict(level_counts)
        
        return analysis

    def plot_log_characteristics(self, log_type: str, analysis: Dict):
        """Plot key characteristics of the log data."""
        plt.figure(figsize=(15, 5))
        
        # Plot 1: Message Length Distribution
        plt.subplot(131)
        lines = self.read_log_sample(log_type)
        lengths = [len(line) for line in lines]
        sns.histplot(lengths, bins=30)
        plt.title(f'{log_type} Log Message Length Distribution')
        plt.xlabel('Message Length')
        plt.ylabel('Count')
        
        # Plot 2: Log Levels Distribution
        if analysis.get('log_levels'):
            plt.subplot(132)
            levels = list(analysis['log_levels'].keys())
            counts = list(analysis['log_levels'].values())
            plt.bar(levels, counts)
            plt.title(f'{log_type} Log Levels Distribution')
            plt.xticks(rotation=45)
            
        plt.tight_layout()
        plt.show()

def main():
    """
    Main execution function.
    
    This function demonstrates the typical workflow for using the LogAnalyzer:
    1. Create an analyzer instance
    2. Read all log files
    3. Parse logs into structured format
    4. Perform analysis on all datasets
    """
    base_path = "model-drift-detection/datasets/raw_drift_dataset"
    analyzer = LogAnalyzer(base_path)
    
    # Analyze each log type
    for log_type in ['HDFS', 'Apache', 'HealthApp', 'BGL', 'HPC', 'Linux', 'Mac']:
        print(f"\nAnalyzing {log_type} logs:")
        analysis = analyzer.analyze_log_structure(log_type)
        if analysis:
            print(f"Total sample lines: {analysis['total_lines']}")
            print(f"Message length: min={analysis['min_length']}, avg={analysis['avg_length']:.2f}, max={analysis['max_length']}")
            print("\nSample entries:")
            for entry in analysis['sample_entries']:
                print(f"  {entry[:100]}...")  # Show first 100 chars
            
            if analysis.get('timestamp_format'):
                print(f"\nDetected timestamp format: {analysis['timestamp_format']}")
            
            if analysis.get('log_levels'):
                print("\nLog level distribution:")
                for level, count in analysis['log_levels'].items():
                    print(f"  {level}: {count}")
            
            analyzer.plot_log_characteristics(log_type, analysis)

if __name__ == "__main__":
    main() 