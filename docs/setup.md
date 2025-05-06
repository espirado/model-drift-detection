# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd model-drift-detection
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Required Packages

The project requires the following main packages:
- pandas>=2.2.0
- numpy>=1.24.0
- matplotlib>=3.10.0
- seaborn>=0.13.0
- scikit-learn>=1.3.0
- jupyter>=1.0.0
- ipykernel>=6.29.0

## Data Setup

1. Ensure the raw log datasets are placed in the correct directories:
```
datasets/raw_drift_dataset/
├── Apache/
├── BGL/
├── HDFS/
├── HealthApp/
├── HPC/
├── Linux/
└── Mac/
```

2. Create necessary directories for processed data:
```bash
mkdir -p datasets/processed
```

## Configuration

1. System Configuration:
   - Copy `config/config.example.yaml` to `config/config.yaml`
   - Update parameters according to your environment

2. Environment Variables:
   - Create a `.env` file in the project root
   - Set required environment variables:
     ```
     LOG_LEVEL=INFO
     DATA_DIR=datasets/raw_drift_dataset
     PROCESSED_DIR=datasets/processed
     ```

## Development Environment Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Configure IDE settings:
   - Set Python interpreter to virtual environment
   - Enable linting (flake8, pylint)
   - Configure code formatting (black)

## Testing Environment

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Run tests:
```bash
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. Package Installation Errors:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --no-cache-dir
   ```

2. Virtual Environment Issues:
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Data Directory Permissions:
   ```bash
   chmod -R 755 datasets/
   ```

### Support

For additional support:
1. Check the issues section in the repository
2. Contact the development team
3. Refer to the documentation in `docs/`

## Next Steps

After completing the setup:
1. Review the user guide in `docs/user-guide/`
2. Explore example notebooks in `notebooks/`
3. Run initial tests to verify setup
4. Start with data preprocessing using the provided scripts 