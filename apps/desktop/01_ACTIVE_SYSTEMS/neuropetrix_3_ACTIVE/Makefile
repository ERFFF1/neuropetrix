PY=python
BACKEND=backend.main:app
TEST_SCHEMA=03_Teknik_Mimari_ve_Yapay_Zeka_Modelleri/Test_Senaryolari/test_schema_validation.sh

# NeuroPETrix v2.0 Makefile
# AI-Powered PET-CT Analysis Platform

.PHONY: help install run-backend run-frontend run-all clean test build

# Default target
help:
	@echo "🧠 NeuroPETrix v2.0 - AI-Powered PET-CT Analysis Platform"
	@echo "========================================================"
	@echo ""
	@echo "📋 Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install        - Install all dependencies"
	@echo "  make run-backend    - Start FastAPI backend"
	@echo "  make run-frontend   - Start Streamlit frontend"
	@echo "  make run-all        - Start both backend and frontend"
	@echo "  make start          - Alias for run-all"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev-install    - Install development dependencies"
	@echo "  make dev-setup      - Setup development environment"
	@echo "  make test           - Run tests"
	@echo "  make build          - Build production version"
	@echo ""
	@echo "🤖 AI Components:"
	@echo "  make install-ai     - Install AI-specific packages (MONAI, PyRadiomics)"
	@echo "  make test-ai        - Test AI pipeline components"
	@echo ""
	@echo "🗄️  Database:"
	@echo "  make db-init        - Initialize database"
	@echo "  make db-reset       - Reset database"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""
	@echo "📊 System:"
	@echo "  make status         - Check system status"
	@echo "  make clean          - Clean temporary files"
	@echo "  make demo           - Run demo script"
	@echo ""

# Installation
install:
	@echo "📦 Installing NeuroPETrix dependencies..."
	pip install -r backend/requirements.txt
	@echo "✅ Installation completed!"

install-ai:
	@echo "🤖 Installing AI-specific packages..."
	pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	pip install monai pyradiomics scikit-learn scikit-image opencv-python
	@echo "✅ AI packages installed!"

# Development setup
dev-install:
	@echo "🔧 Installing development dependencies..."
	pip install -r backend/requirements.txt
	pip install pytest black flake8 mypy
	@echo "✅ Development dependencies installed!"

dev-setup:
	@echo "⚙️  Setting up development environment..."
	python -m venv venv
	@echo "✅ Development environment ready!"

# Running the application
run-backend:
	@echo "🚀 Starting NeuroPETrix Backend (FastAPI)..."
	@echo "📍 Backend will be available at: http://127.0.0.1:8000"
	@echo "📚 API Documentation: http://127.0.0.1:8000/docs"
	@echo "🔍 Health Check: http://127.0.0.1:8000/health"
	@echo ""
	cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

run-frontend:
	@echo "🌐 Starting NeuroPETrix Frontend (Streamlit)..."
	@echo "📍 Frontend will be available at: http://127.0.0.1:8501"
	@echo "🎭 Demo mode is automatically active"
	@echo ""
	cd "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod" && streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1

run-all:
	@echo "🚀 Starting NeuroPETrix v2.0 (Backend + Frontend)..."
	@echo "📍 Backend: http://127.0.0.1:8000"
	@echo "📍 Frontend: http://127.0.0.1:8501"
	@echo "🎭 Demo mode is automatically active"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@echo ""
	@make run-backend & make run-frontend

start: run-all

# Testing
test:
	@echo "🧪 Running NeuroPETrix tests..."
	python -m pytest tests/ -v
	@echo "✅ Tests completed!"

test-ai:
	@echo "🤖 Testing AI pipeline components..."
	python -c "import torch; print(f'PyTorch: {torch.__version__}')"
	python -c "import monai; print(f'MONAI: {monai.__version__}')"
	python -c "import radiomics; print(f'PyRadiomics: {radiomics.__version__}')"
	@echo "✅ AI components test completed!"

# Database operations
db-init:
	@echo "🗄️  Initializing NeuroPETrix database..."
	cd backend && python -c "from main import init_db; init_db(); print('Database initialized!')"
	@echo "✅ Database initialized!"

db-reset:
	@echo "🔄 Resetting NeuroPETrix database..."
	rm -f backend/neuropetrix.db
	@make db-init
	@echo "✅ Database reset completed!"

# Building and deployment
build:
	@echo "🏗️  Building NeuroPETrix production version..."
	pip install -r backend/requirements.txt
	@echo "✅ Build completed!"

# Docker operations
docker-build:
	@echo "🐳 Building NeuroPETrix Docker image..."
	docker build -t neuropetrix:v2.0 .
	@echo "✅ Docker image built!"

docker-run:
	@echo "🐳 Running NeuroPETrix Docker container..."
	docker run -p 8000:8000 -p 8501:8501 neuropetrix:v2.0
	@echo "✅ Docker container running!"

# System operations
status:
	@echo "📊 NeuroPETrix System Status:"
	@echo "=============================="
	@echo ""
	@echo "🔍 Checking Backend (Port 8000)..."
	@curl -s http://127.0.0.1:8000/health > /dev/null && echo "✅ Backend: RUNNING" || echo "❌ Backend: STOPPED"
	@echo ""
	@echo "🔍 Checking Frontend (Port 8501)..."
	@curl -s http://127.0.0.1:8501 > /dev/null && echo "✅ Frontend: RUNNING" || echo "❌ Frontend: STOPPED"
	@echo ""
	@echo "📁 Checking Database..."
	@test -f backend/neuropetrix.db && echo "✅ Database: EXISTS" || echo "❌ Database: MISSING"
	@echo ""

clean:
	@echo "🧹 Cleaning NeuroPETrix temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "✅ Cleanup completed!"

# Demo script
demo:
	@echo "🎬 Running NeuroPETrix v2.0 Demo..."
	@chmod +x demo.sh
	./demo.sh

# HBYS Mock Service
hbys-mock:
	@echo "🏥 Starting HBYS Mock Service..."
	@echo "📍 Mock service will be available at: http://127.0.0.1:8001"
	@echo "📚 Mock API Documentation: http://127.0.0.1:8001/docs"
	@echo ""
	cd "04_Uygulama_Gelistirme_ve_UIUX/API_Entegrasyonlari" && python hbys_mock.py

# Cross-platform installation
install-cross:
	@echo "🌍 Installing NeuroPETrix (Cross-platform)..."
	@chmod +x install.sh
	./install.sh

# Production installation and start
prod-install:
	@echo "🏭 Installing NeuroPETrix Production..."
	@make install
	@make install-ai
	@make db-init
	@echo "✅ Production installation completed!"

prod-start:
	@echo "🏭 Starting NeuroPETrix Production..."
	@make run-all

# Help for specific command groups
help-quick:
	@echo "🚀 Quick Start Commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make run-all        - Start both services"
	@echo "  make status         - Check system status"

help-dev:
	@echo "🔧 Development Commands:"
	@echo "  make dev-install    - Install dev dependencies"
	@echo "  make test           - Run tests"
	@echo "  make build          - Build production version"

help-ai:
	@echo "🤖 AI Components Commands:"
	@echo "  make install-ai     - Install AI packages"
	@echo "  make test-ai        - Test AI components"
	@echo "  make db-init        - Initialize database"

help-docker:
	@echo "🐳 Docker Commands:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
