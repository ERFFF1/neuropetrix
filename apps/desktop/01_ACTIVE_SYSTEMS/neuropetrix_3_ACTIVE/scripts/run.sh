#!/bin/bash

echo "🚀 Neuropetrix Monorepo Startup"
echo "================================"

# Check if we're in the right directory
if [ ! -f "apps/backend/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] pydantic-settings sqlalchemy alembic psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart boto3 minio redis rq jinja2 httpx prometheus-fastapi-instrumentator

# Install worker dependencies
echo "📦 Installing worker dependencies..."
pip install pydantic numpy scikit-image Pillow pyradiomics

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p infra/db
mkdir -p apps/backend/reports

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file..."
    cp env.example .env
fi

# Start Redis (if not running)
echo "🔴 Starting Redis..."
if ! pgrep -x "redis-server" > /dev/null; then
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        echo "✅ Redis started"
    else
        echo "⚠️  Redis not found. Please install Redis: brew install redis"
        echo "   Then run: brew services start redis"
    fi
else
    echo "✅ Redis already running"
fi

# Start Backend
echo "📡 Starting Backend API..."
cd apps/backend
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 3

# Start Worker
echo "👷 Starting Worker..."
cd apps/worker
python worker.py &
WORKER_PID=$!
cd ../..

# Start Frontend
echo "🌐 Starting Frontend..."
cd apps/frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ../..

echo ""
echo "✅ All services started!"
echo "📡 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "👷 Worker: Running in background"
echo ""
echo "🛑 To stop all services:"
echo "kill $BACKEND_PID $WORKER_PID $FRONTEND_PID"

# Wait for user to stop
wait
