#!/bin/bash

# Run all tests with coverage

echo "🧪 Running Robot Wall Planner Tests..."
echo ""

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with coverage
pytest tests/ -v --tb=short

echo ""
echo "✅ Tests complete!"
