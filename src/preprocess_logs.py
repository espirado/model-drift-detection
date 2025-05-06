import os
import sys

# Add the src directory to the Python path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(src_dir))

from src.preprocessing.log_preprocessor import LogPreprocessor
from src.config.preprocessing_config import PreprocessingConfig

def read_log_file(file_path):
    """Read log file and return list of lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def main():
    # Initialize preprocessor with default config
    config = PreprocessingConfig()
    preprocessor = LogPreprocessor(config)
    
    # Define paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, 'datasets', 'raw_drift_dataset')
    processed_dir = os.path.join(base_dir, 'datasets', 'processed')
    
    # Process HDFS logs
    hdfs_path = os.path.join(dataset_dir, 'HDFS', 'hdfs.log')
    hdfs_output = os.path.join(processed_dir, 'hdfs_processed.csv')
    print("\nProcessing HDFS logs...")
    try:
        hdfs_logs = read_log_file(hdfs_path)
        hdfs_df = preprocessor.process(hdfs_logs, log_type="hdfs", output_path=hdfs_output)
        print(f"HDFS logs processed successfully - {len(hdfs_df)} time windows created")
    except Exception as e:
        print(f"Error processing HDFS logs: {str(e)}")
    
    # Process Apache logs
    apache_path = os.path.join(dataset_dir, 'Apache', 'Apache.log')
    apache_output = os.path.join(processed_dir, 'apache_processed.csv')
    print("\nProcessing Apache logs...")
    try:
        apache_logs = read_log_file(apache_path)
        apache_df = preprocessor.process(apache_logs, log_type="apache", output_path=apache_output)
        print(f"Apache logs processed successfully - {len(apache_df)} time windows created")
    except Exception as e:
        print(f"Error processing Apache logs: {str(e)}")
    
    # Process HealthApp logs
    health_path = os.path.join(dataset_dir, 'HealthApp', 'HealthApp.log')
    health_output = os.path.join(processed_dir, 'healthapp_processed.csv')
    print("\nProcessing HealthApp logs...")
    try:
        health_logs = read_log_file(health_path)
        health_df = preprocessor.process(health_logs, log_type="healthapp", output_path=health_output)
        print(f"HealthApp logs processed successfully - {len(health_df)} time windows created")
    except Exception as e:
        print(f"Error processing HealthApp logs: {str(e)}")

if __name__ == "__main__":
    main() 