#!/bin/bash

# Meeting & Lecture Summarizer - React Frontend Startup Script

echo "🎤 Starting Meeting & Lecture Summarizer (React Frontend)"
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Node.js dependencies for React frontend
echo "📦 Installing React frontend dependencies..."
cd frontend
npm install
cd ..

# Start Weaviate (optional)
if command -v docker &> /dev/null; then
    echo "🐳 Starting Weaviate with Docker..."
    docker run -d \
        --name weaviate-summarizer \
        -p 8080:8080 \
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
        -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
        semitechnologies/weaviate:latest
    
    echo "⏳ Waiting for Weaviate to start..."
    sleep 10
else
    echo "⚠️  Docker not found. Weaviate will not be started. Install Docker or use Weaviate Cloud Service."
fi

# Start the FastAPI backend
echo "🚀 Starting FastAPI backend..."
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start the React frontend
echo "🚀 Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Application started successfully!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker stop weaviate-summarizer 2>/dev/null; exit" INT
wait
