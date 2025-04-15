#!/bin/bash
# Model Drift Detection System Runner
# Usage: ./run.sh [component]
# Example: ./run.sh all
# Example: ./run.sh dashboard

component=$1

if [ "$component" = "all" ] || [ -z "$component" ]; then
    echo "Starting all components..."
    # Start commands would go here
elif [ "$component" = "dashboard" ]; then
    echo "Starting dashboard..."
    # Dashboard startup command would go here
elif [ "$component" = "producer" ]; then
    echo "Starting data producer..."
    # Producer startup command would go here
else
    echo "Unknown component: $component"
    echo "Available components: all, dashboard, producer"
    exit 1
fi
