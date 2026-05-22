#!/bin/bash

# Quick run script (assumes dependencies already installed)

# Set PYTHONPATH to include current directory and Server
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"

# Check if database is initialized
if [ ! -f "robot_planner.db" ]; then
    echo "🗄️  Database not found. Running migrations..."
    python db/migrate.py migrate
    if [ $? -ne 0 ]; then
        echo "❌ Migration failed! Exiting..."
        exit 1
    fi
fi

# Run the server
uvicorn Server.main:app --reload --host 0.0.0.0 --port 8000
