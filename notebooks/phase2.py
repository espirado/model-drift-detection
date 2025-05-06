#!/usr/bin/env python
# coding: utf-8

# In[27]:


# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re
from datetime import datetime
import chardet  # For detecting file encoding
from collections import defaultdict, Counter
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

# Set up basic visualization settings
plt.style.use('default')
sns.set()
get_ipython().run_line_magic('matplotlib', 'inline')

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet"""
    with open(file_path, 'rb') as file:
        # Read a sample of the file to detect encoding
        raw_data = file.read(10000)  # Read first 10000 bytes
        result = chardet.detect(raw_data)
        return result['encoding']


# In[5]:


pip install chardet 


# In[22]:


# Define paths
base_path = Path('../datasets/raw_drift_dataset')
hdfs_path = base_path / 'HDFS' / 'hdfs.log'
apache_path = base_path / 'Apache' / 'Apache.log'
health_path = base_path / 'HealthApp' / 'HealthApp.log'
bgl_path = base_path / 'BGL' / 'BGL.log'
hpc_path = base_path / 'HPC' / 'HPC.log'
linux_path = base_path / 'Linux' / 'Linux.log'
mac_path = base_path / 'Mac' / 'Mac.log'

def read_logs(file_path):
    """Read log files and return non-empty lines."""
    # Try different encodings
    encodings = ['utf-8', 'latin1', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except UnicodeDecodeError:
            continue

    # If all encodings fail, use latin1 with error replacement
    with open(file_path, 'r', encoding='latin1', errors='replace') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Read logs
print("Reading log files...")
hdfs_logs = read_logs(hdfs_path)
apache_logs = read_logs(apache_path)
health_logs = read_logs(health_path)
bgl_logs = read_logs(bgl_path)
hpc_logs = read_logs(hpc_path)
linux_logs = read_logs(linux_path)
mac_logs = read_logs(mac_path)

print(f"HDFS Logs: {len(hdfs_logs)} entries")
print(f"Apache Logs: {len(apache_logs)} entries")
print(f"HealthApp Logs: {len(health_logs)} entries")
print(f"BGL Logs: {len(bgl_logs)} entries")
print(f"HPC Logs: {len(hpc_logs)} entries")
print(f"Linux Logs: {len(linux_logs)} entries")
print(f"Mac Logs: {len(mac_logs)} entries")

# Show samples
print("\nSample log entries:")
for name, logs in [
    ("HDFS", hdfs_logs), 
    ("Apache", apache_logs), 
    ("HealthApp", health_logs),
    ("BGL", bgl_logs),
    ("HPC", hpc_logs),
    ("Linux", linux_logs),
    ("Mac", mac_logs)
]:
    print(f"\n{name} samples:")
    for log in logs[:3]:
        print(f"- {log}")


# In[39]:


def analyze_log_structure(name: str, logs: List[str]):
    """Analyze the structure and characteristics of log entries"""
    print(f"\n{'='*20} Log Structure Analysis: {name} {'='*20}")

    # Basic statistics
    lengths = [len(log) for log in logs]

    print(f"\nBasic Statistics:")
    print(f"Total entries: {len(logs)}")
    print(f"Average length: {np.mean(lengths):.2f} characters")
    print(f"Min length: {min(lengths)} characters")
    print(f"Max length: {max(lengths)} characters")

    # Visualize length distribution
    plt.figure(figsize=(15, 5))

    plt.subplot(131)
    sns.histplot(lengths, bins=50)
    plt.title(f"{name} Log Length Distribution")
    plt.xlabel("Entry Length (characters)")
    plt.ylabel("Count")

    plt.subplot(132)
    sns.boxplot(y=lengths)
    plt.title(f"{name} Length Box Plot")
    plt.ylabel("Entry Length")

    plt.subplot(133)
    sns.kdeplot(lengths)
    plt.title(f"{name} Length Density")
    plt.xlabel("Entry Length")

    plt.tight_layout()
    plt.show()

analyze_log_structure("HDFS", hdfs_logs)
analyze_log_structure("Apache", apache_logs)
analyze_log_structure("HealthApp", health_logs)
analyze_log_structure("BGL", bgl_logs)
analyze_log_structure("HPC", hpc_logs)
analyze_log_structure("Linux", linux_logs)
analyze_log_structure("Mac", mac_logs)



# In[40]:


def analyze_message_types(name: str, logs: List[str]):
    """Analyze different types of messages and their patterns"""
    print(f"\n{'='*20} Message Type Analysis: {name} {'='*20}")

    # Define patterns for different message types
    patterns = {
        'Error': r'error|ERROR|Error|FAIL|fail|Fail|EXCEPTION|exception|Exception',
        'Warning': r'warn|WARN|Warn|WARNING|warning|Warning',
        'Info': r'info|INFO|Info|NOTICE|notice|Notice',
        'Debug': r'debug|DEBUG|Debug|TRACE|trace|Trace',
        'Critical': r'critical|CRITICAL|Critical|FATAL|fatal|Fatal|EMERGENCY|emergency|Emergency'
    }

    # Count occurrences
    type_counts = {type_name: sum(1 for log in logs if re.search(pattern, log)) 
                  for type_name, pattern in patterns.items()}

    # Calculate percentages
    total = len(logs)
    percentages = {type_name: (count/total)*100 for type_name, count in type_counts.items()}

    print("\nMessage Type Distribution:")
    for type_name, count in type_counts.items():
        print(f"{type_name}: {count} ({percentages[type_name]:.2f}%)")

    # Visualizations
    plt.figure(figsize=(15, 5))

    plt.subplot(131)
    plt.bar(type_counts.keys(), type_counts.values())
    plt.title(f"{name} Message Types")
    plt.xticks(rotation=45)
    plt.ylabel("Count")

    plt.subplot(132)
    plt.pie(percentages.values(), labels=percentages.keys(), autopct='%1.1f%%')
    plt.title("Message Type Distribution")

    # Message length by type
    plt.subplot(133)
    type_lengths = defaultdict(list)
    for log in logs:
        for type_name, pattern in patterns.items():
            if re.search(pattern, log):
                type_lengths[type_name].append(len(log))
                break

    plt.boxplot([lengths for lengths in type_lengths.values()], labels=type_lengths.keys())
    plt.title("Message Length by Type")
    plt.xticks(rotation=45)
    plt.ylabel("Length")

    plt.tight_layout()
    plt.show()

# Example usage:
analyze_message_types("HDFS", hdfs_logs)
analyze_message_types("Apache", apache_logs)
analyze_message_types("HealthApp", health_logs)
analyze_message_types("BGL", bgl_logs)
analyze_message_types("HPC", hpc_logs)
analyze_message_types("Linux", linux_logs)
analyze_message_types("Mac", mac_logs)


# In[43]:


def analyze_temporal_patterns(name: str, logs: List[str]):
    """Analyze temporal patterns in log entries"""
    print(f"\n{'='*20} Temporal Pattern Analysis: {name} {'='*20}")

    # Extended timestamp patterns
    timestamp_patterns = [
        # HDFS format (e.g., "081109 203518" for Nov 9, 2008 20:35:18)
        (r'(\d{6}\s+\d{6})', '%y%m%d %H%M%S'),
        # ISO format
        (r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S'),
        # Syslog format
        (r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
        # Common log format
        (r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', '%m/%d/%Y %H:%M:%S'),
        # Apache format
        (r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})', '%d/%b/%Y:%H:%M:%S')
    ]

    timestamps = []
    for log in logs:
        for pattern, time_format in timestamp_patterns:
            match = re.search(pattern, log)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # For HDFS format, add century (assuming 20xx)
                    if len(timestamp_str) == 13 and ' ' in timestamp_str:  # HDFS format
                        timestamp = datetime.strptime(f"20{timestamp_str}", '%Y%m%d %H%M%S')
                    else:
                        timestamp = datetime.strptime(timestamp_str, time_format)
                    timestamps.append(timestamp)
                    break
                except ValueError:
                    continue

    if timestamps:
        print(f"\nTemporal Statistics:")
        print(f"Timestamps found: {len(timestamps)}")
        print(f"Time range: {min(timestamps)} to {max(timestamps)}")

        # Calculate time differences
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                     for i in range(len(timestamps)-1)]

        if time_diffs:
            print(f"Average time between logs: {np.mean(time_diffs):.2f} seconds")
            print(f"Min time between logs: {min(time_diffs):.2f} seconds")
            print(f"Max time between logs: {max(time_diffs):.2f} seconds")

        # Visualizations
        plt.figure(figsize=(15, 5))

        plt.subplot(131)
        hours = [t.hour for t in timestamps]
        plt.hist(hours, bins=24, range=(0,24))
        plt.title(f"{name} Hourly Distribution")
        plt.xlabel("Hour of Day")
        plt.ylabel("Count")

        if time_diffs:
            plt.subplot(132)
            plt.hist(time_diffs, bins=50)
            plt.title("Time Between Logs")
            plt.xlabel("Seconds")
            plt.ylabel("Count")

        plt.subplot(133)
        plt.plot(timestamps, range(len(timestamps)))
        plt.title("Cumulative Logs Over Time")
        plt.xlabel("Time")
        plt.ylabel("Count")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

        # Additional temporal patterns
        print("\nTemporal Patterns:")
        days = [t.day for t in timestamps]
        months = [t.month for t in timestamps]
        weekdays = [t.weekday() for t in timestamps]

        print(f"Most common hours: {Counter(hours).most_common(3)}")
        print(f"Most common days: {Counter(days).most_common(3)}")
        print(f"Most common months: {Counter(months).most_common(3)}")
        print(f"Most common weekdays: {Counter(weekdays).most_common(3)}")  # 0=Monday, 6=Sunday

    else:
        print("No timestamps found in the logs")
        # Print first few log entries to help debug timestamp extraction
        print("\nFirst few log entries for format reference:")
        for log in logs[:3]:
            print(f"- {log}")

# Example usage:
analyze_temporal_patterns("HDFS", hdfs_logs)
analyze_temporal_patterns("Apache", apache_logs)
analyze_temporal_patterns("HealthApp", health_logs)
analyze_temporal_patterns("BGL", bgl_logs)
analyze_temporal_patterns("HPC", hpc_logs)
analyze_temporal_patterns("Linux", linux_logs)
analyze_temporal_patterns("Mac", mac_logs)


# In[44]:


def analyze_components(name: str, logs: List[str]):
    """Analyze system components mentioned in logs"""
    print(f"\n{'='*20} Component Analysis: {name} {'='*20}")

    # Extract components using various patterns
    components = []
    for log in logs:
        # HDFS specific patterns
        # Look for components in various formats:
        # - Words between square brackets: [ComponentName]
        # - Words before a colon: ComponentName:
        # - Words after "INFO"/"ERROR"/"WARN": INFO ComponentName:
        # - Process/Thread IDs: (ProcessName_123)
        patterns = [
            r'\[(.*?)\]',                          # [Component]
            r'^([A-Za-z0-9_-]+):',                 # Component:
            r'(?:INFO|ERROR|WARN)\s+([^:]+):',     # INFO Component:
            r'\(([\w.-]+)\)',                      # (Component)
            r'(?:daemon|server|client)\s+([\w.-]+)',  # daemon/server/client names
            r'blk_[-\d]+',                         # HDFS block IDs
            r'BP-[\d\-]+',                         # HDFS block pool IDs
            r'DFSClient_[\w.-]+',                  # DFS Client IDs
            r'NameNode',                           # NameNode references
            r'DataNode',                           # DataNode references
            r'FSNamesystem',                       # FSNamesystem references
            r'PacketResponder',                    # PacketResponder references
        ]

        for pattern in patterns:
            found = re.findall(pattern, log)
            components.extend([comp for comp in found if comp])  # Add non-empty matches

    if components:
        component_counts = Counter(components)

        print(f"\nComponent Statistics:")
        print(f"Unique components: {len(component_counts)}")
        print("\nTop 10 components:")
        for comp, count in component_counts.most_common(10):
            print(f"{comp}: {count}")

        # Visualizations
        plt.figure(figsize=(15, 5))

        # Top components bar plot
        plt.subplot(131)
        top_comps = dict(component_counts.most_common(10))
        plt.bar(range(len(top_comps)), list(top_comps.values()))
        plt.xticks(range(len(top_comps)), list(top_comps.keys()), rotation=45, ha='right')
        plt.title(f"{name} Top Components")
        plt.ylabel("Count")

        # Component name length distribution
        plt.subplot(132)
        comp_lengths = [len(comp) for comp in components]
        plt.hist(comp_lengths, bins=30)
        plt.title("Component Name Lengths")
        plt.xlabel("Length")
        plt.ylabel("Count")

        # Top 5 components pie chart
        plt.subplot(133)
        top_5_comps = dict(component_counts.most_common(5))
        plt.pie(list(top_5_comps.values()), 
                labels=list(top_5_comps.keys()), 
                autopct='%1.1f%%')
        plt.title("Top 5 Components Distribution")

        plt.tight_layout()
        plt.show()

        # Additional component analysis
        print("\nComponent Categories:")

        # Categorize components
        node_components = sum(1 for comp in components if 'Node' in comp)
        system_components = sum(1 for comp in components if 'System' in comp)
        client_components = sum(1 for comp in components if 'Client' in comp)
        block_components = sum(1 for comp in components if 'blk_' in comp)

        print(f"Node-related components: {node_components}")
        print(f"System-related components: {system_components}")
        print(f"Client-related components: {client_components}")
        print(f"Block-related components: {block_components}")

    else:
        print("No components found in the logs")
        print("\nSample log entries for format reference:")
        for log in logs[:3]:
            print(f"- {log}")

# Example usage:
analyze_components("HDFS", hdfs_logs)
analyze_components("Apache", apache_logs)
analyze_components("HealthApp", health_logs)
analyze_components("BGL", bgl_logs)
analyze_components("HPC", hpc_logs)
analyze_components("Linux", linux_logs)
analyze_components("Mac", mac_logs)


# In[35]:





# In[36]:


for log_type in log_paths.keys():
    print(f"\nAnalyzing {log_type} logs...")
    logs = read_log_sample(log_type, sample_size=1000)  # Adjust sample size as needed

    analyze_temporal_patterns(logs, log_type)
    analyze_components(logs, log_type)
    analyze_patterns(logs, log_type)
    analyze_errors(logs, log_type)


# In[ ]:




