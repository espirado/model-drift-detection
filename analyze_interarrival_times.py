import re
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plot_dir = Path("eda_plots")
plot_dir.mkdir(exist_ok=True)

def extract_timestamps_by_dataset(logs, dataset):
    timestamps = []
    if dataset == "HDFS":
        for log in logs:
            match = re.match(r'(\d{6} \d{6})', log)
            if match:
                try:
                    ts = datetime.strptime(match.group(1), "%y%m%d %H%M%S")
                    timestamps.append(ts)
                except Exception:
                    continue
    elif dataset == "APACHE":
        for log in logs:
            match = re.search(r'\[([A-Za-z]{3} [A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2} \d{4})\]', log)
            if match:
                try:
                    ts = datetime.strptime(match.group(1), "%a %b %d %H:%M:%S %Y")
                    timestamps.append(ts)
                except Exception:
                    continue
    elif dataset == "BGL":
        for log in logs:
            match = re.search(r'(\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+)', log)
            if match:
                try:
                    ts = datetime.strptime(match.group(1), "%Y-%m-%d-%H.%M.%S.%f")
                    timestamps.append(ts)
                except Exception:
                    continue
    elif dataset == "HEALTHAPP":
        for log in logs:
            match = re.match(r'(\d{8}-\d{2}:\d{2}:\d{2}):\d{3}', log)
            if match:
                try:
                    ts = datetime.strptime(match.group(1), "%Y%m%d-%H:%M:%S")
                    timestamps.append(ts)
                except Exception:
                    continue
    elif dataset == "HPC":
        for log in logs:
            match = re.search(r'(\d{10})', log)
            if match:
                try:
                    ts = datetime.fromtimestamp(int(match.group(1)))
                    timestamps.append(ts)
                except Exception:
                    continue
    elif dataset == "LINUX" or dataset == "MAC":
        for log in logs:
            match = re.match(r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', log)
            if match:
                try:
                    ts = datetime.strptime(match.group(1) + " 2000", "%b %d %H:%M:%S %Y")
                    timestamps.append(ts)
                except Exception:
                    continue
    return sorted(timestamps)

def analyze_interarrival_times(logs, name):
    timestamps = extract_timestamps_by_dataset(logs, name.upper())
    if len(timestamps) > 1:
        interarrivals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        print(f"\n{name} Inter-Arrival Time Stats:")
        print(f"  Min: {min(interarrivals):.2f} sec")
        print(f"  Max: {max(interarrivals):.2f} sec")
        print(f"  Mean: {np.mean(interarrivals):.2f} sec")
        print(f"  Std: {np.std(interarrivals):.2f} sec")
        plt.figure(figsize=(12, 4))
        sns.histplot(interarrivals, bins=50, kde=True)
        plt.title(f"{name} Inter-Arrival Time Distribution")
        plt.xlabel("Seconds Between Entries")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(plot_dir / f"{name.lower()}_interarrival_times.png")
        plt.show()
    else:
        print(f"{name}: Not enough timestamps for inter-arrival analysis.")

# Example usage (assume log lists are defined elsewhere):
# analyze_interarrival_times(hdfs_logs, "HDFS")
# analyze_interarrival_times(apache_logs, "APACHE")
# analyze_interarrival_times(bgl_logs, "BGL")
# analyze_interarrival_times(healthapp_logs, "HEALTHAPP")
# analyze_interarrival_times(hpc_logs, "HPC")
# analyze_interarrival_times(linux_logs, "LINUX")
# analyze_interarrival_times(mac_logs, "MAC") 