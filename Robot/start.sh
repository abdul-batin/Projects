#!/bin/bash

# Startup script for Robot Wall Planner API

echo "🤖 Starting Robot Wall Planner API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Checking database migrations..."
python db/migrate.py status > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📊 Running database migrations..."
    python db/migrate.py migrate
    if [ $? -ne 0 ]; then
        echo "❌ Migration failed! Exiting..."
        exit 1
    fi
    echo "✅ Database initialized successfully"
else
    echo "✅ Database already initialized"
fi

# Set PYTHONPATH to include Robot and Server directories
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"

# Start the server from Robot directory
echo "🚀 Starting FastAPI server..."
echo "📖 API Docs will be available at: http://localhost:8000/docs"
echo ""

uvicorn Server.main:app --reload --host 0.0.0.0 --port 8000
