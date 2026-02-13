#!/bin/bash
# Setup script for TOEFL Listening Backend

echo "🚀 TOEFL Listening Backend Setup"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p static/ListeningItems

# Run migrations
echo "🗄️  Running database migrations..."
python migrations/run_migration.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or with Docker:"
echo "  docker-compose up -d"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/api/docs"
