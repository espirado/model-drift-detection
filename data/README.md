# Dataset Documentation

## Overview

This directory contains sample datasets for testing the drift detection system.

## Synthetic Drift Dataset

A generated dataset with controlled drift patterns:

- **Phase 1**: Baseline distributions
- **Phase 2**: Sudden drift in numeric features
- **Phase 3**: Categorical distribution shift
- **Phase 4**: Gradual drift and concept drift

## Feature Descriptions

- **feature1**: Numeric feature (normal distribution)
- **feature2**: Numeric feature (exponential distribution)
- **feature3**: Categorical feature with 4 classes

## Data Generation

The datasets are generated with intentional drift patterns to test detection algorithms.

## Data Quality Issues

The raw datasets include:
- Missing values
- Format inconsistencies
- Outliers
- Mixed data types
