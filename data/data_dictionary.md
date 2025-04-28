# Data Dictionary

This document provides detailed information about the data fields, preprocessing steps, and quality considerations for each log dataset used in the system reliability drift detection project.

## Common Fields Across All Datasets

### Timestamp
- **Description**: When the log entry was generated
- **Data Type**: DateTime
- **Format**: YYYY-MM-DD HH:MM:SS.mmm
- **Example**: "2023-01-01 12:34:56.789"
- **Constraints**: Must be in valid datetime format
- **Notes**: Primary key for the dataset
- **Data Quality**: Complete field, consistent format
- **Preprocessing**: 
  - Standardized to UTC timezone
  - Parsed to datetime objects
  - Missing timestamps are flagged for review

### Component
- **Description**: System component that generated the log
- **Data Type**: String
- **Format**: Alphanumeric
- **Example**: "DataNode", "NameNode", "HttpServer"
- **Constraints**: Non-null
- **Notes**: Used for component-level analysis
- **Data Quality**: Complete field, controlled vocabulary
- **Preprocessing**:
  - Standardized to lowercase
  - Mapped to consistent component names
  - Unknown components flagged for review

### Severity
- **Description**: Log level indicating message importance
- **Data Type**: Categorical
- **Values**: ["INFO", "WARNING", "ERROR", "CRITICAL", "DEBUG"]
- **Example**: "ERROR"
- **Constraints**: Must be one of predefined levels
- **Notes**: Used for error rate analysis
- **Data Quality**: Standardized levels across systems
- **Preprocessing**:
  - Normalized to standard levels
  - Missing levels defaulted to "INFO"
  - Non-standard levels mapped to closest standard

### Message
- **Description**: Actual log message content
- **Data Type**: String
- **Format**: Free text
- **Example**: "Block blk_123 is missing from node node_456"
- **Constraints**: Non-null
- **Notes**: Contains key information for pattern analysis
- **Data Quality**: Variable format, may contain noise
- **Preprocessing**:
  - Removed special characters
  - Tokenized for pattern matching
  - Variables extracted using regex
  - Template patterns identified

## Dataset-Specific Fields

### HDFS Logs
#### Block ID
- **Description**: Unique identifier for HDFS blocks
- **Data Type**: String
- **Format**: "blk_" followed by numbers
- **Example**: "blk_123456789"
- **Extraction**: Regex pattern `blk_\d+`
- **Preprocessing**:
  - Extracted from message field
  - Validated for correct format
  - Missing IDs tracked separately

#### Node ID
- **Description**: Identifier for HDFS nodes
- **Data Type**: String
- **Format**: Various node naming patterns
- **Example**: "node_123", "datanode_456"
- **Extraction**: Custom regex patterns
- **Preprocessing**:
  - Standardized node naming
  - IP addresses anonymized
  - Location info preserved

### Apache Web Server Logs
#### HTTP Method
- **Description**: HTTP request method
- **Data Type**: Categorical
- **Values**: ["GET", "POST", "PUT", "DELETE", etc.]
- **Example**: "GET"
- **Extraction**: First word in request field
- **Preprocessing**:
  - Validated against HTTP standards
  - Non-standard methods flagged

#### Status Code
- **Description**: HTTP response status code
- **Data Type**: Integer
- **Format**: 3-digit codes
- **Example**: 404, 500
- **Constraints**: Valid HTTP status codes
- **Preprocessing**:
  - Grouped by category (2xx, 4xx, 5xx)
  - Invalid codes flagged

### HealthApp Logs
#### User ID
- **Description**: Anonymous user identifier
- **Data Type**: String
- **Format**: UUID
- **Example**: "user_123abc"
- **Preprocessing**:
  - Consistent hashing applied
  - PII removed
  - Session tracking enabled

#### Action Type
- **Description**: Type of user action
- **Data Type**: Categorical
- **Values**: ["login", "logout", "data_access", etc.]
- **Example**: "login"
- **Preprocessing**:
  - Standardized action names
  - Grouped by category
  - Frequency analysis applied

### OpenSSH Logs
#### Session ID
- **Description**: Unique session identifier
- **Data Type**: String
- **Format**: Alphanumeric
- **Example**: "session_123xyz"
- **Preprocessing**:
  - Extracted from connection logs
  - Linked to auth attempts
  - Duration calculated

#### Authentication Type
- **Description**: Method of authentication
- **Data Type**: Categorical
- **Values**: ["password", "key", "certificate"]
- **Example**: "key"
- **Preprocessing**:
  - Standardized auth methods
  - Failed attempts tracked
  - Pattern analysis applied

## Preprocessing Pipeline

1. **Initial Parsing**
   ```python
   def parse_log_line(line):
       return {
           'timestamp': extract_timestamp(line),
           'component': extract_component(line),
           'severity': extract_severity(line),
           'message': extract_message(line)
       }
   ```

2. **Field Extraction**
   ```python
   def extract_fields(parsed_log):
       dataset_specific_fields = {
           'hdfs': extract_hdfs_fields,
           'apache': extract_apache_fields,
           'healthapp': extract_healthapp_fields,
           'ssh': extract_ssh_fields
       }
       return dataset_specific_fields[dataset_type](parsed_log)
   ```

3. **Data Quality Checks**
   ```python
   def validate_log_entry(entry):
       checks = [
           validate_timestamp,
           validate_component,
           validate_severity,
           validate_required_fields
       ]
       return all(check(entry) for check in checks)
   ```

4. **Feature Engineering**
   ```python
   def engineer_features(parsed_logs):
       return {
           'error_rate': calculate_error_rate(parsed_logs),
           'component_distribution': get_component_dist(parsed_logs),
           'message_patterns': extract_patterns(parsed_logs),
           'temporal_features': extract_temporal_features(parsed_logs)
       }
   ```

## Data Quality Metrics

- **Completeness**: Percentage of non-null values
- **Consistency**: Pattern adherence rate
- **Timeliness**: Timestamp lag statistics
- **Accuracy**: Field validation success rate
- **Uniqueness**: Duplicate entry statistics

## Usage Notes

1. **Sampling Strategy**
   - Random sampling for large datasets
   - Stratified sampling by severity
   - Time-based windows for streaming

2. **Missing Data Handling**
   - Timestamp: Drop entries
   - Component: Use "unknown"
   - Severity: Default to "INFO"
   - Message: Flag for review

3. **Pattern Detection**
   - Log template extraction
   - Variable identification
   - Frequency analysis
   - Anomaly detection baselines 