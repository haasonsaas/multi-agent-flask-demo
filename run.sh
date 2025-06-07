#!/bin/bash
# Flask Dashboard API Startup Script

echo "Starting Flask Dashboard API..."

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "Loaded environment variables from .env"
fi

# Set default values if not provided
export FLASK_APP=${FLASK_APP:-app.py}
export FLASK_ENV=${FLASK_ENV:-development}
export PORT=${PORT:-5000}

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
if [ ! -f ".requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    touch .requirements_installed
fi

# Create results directory if it doesn't exist
mkdir -p results

echo "Starting Flask server on port $PORT..."
echo "API will be available at http://localhost:$PORT/api"
echo "Health check endpoint: http://localhost:$PORT/health"
echo ""

# Run the Flask application
python app.py