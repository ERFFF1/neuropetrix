#!/bin/bash

# NeuroPETRIX Production Deployment Script
# This script deploys the complete NeuroPETRIX system to production

set -e

echo "🚀 NeuroPETRIX Production Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs/nginx
mkdir -p logs/backend
mkdir -p logs/frontend
mkdir -p uploads
mkdir -p backups
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p monitoring/rules
mkdir -p nginx/ssl

# Set permissions
chmod 755 logs
chmod 755 uploads
chmod 755 backups

# Check if .env file exists
if [ ! -f .env.production ]; then
    print_warning ".env.production file not found. Creating from template..."
    cat > .env.production << EOF
# Production Environment Variables
APP_ENV=production
JWT_SECRET=your_very_secure_production_jwt_secret_key_here
JWT_EXPIRES_MIN=120
DATABASE_URL=postgresql://neuropetrix:secure_password@db:5432/neuropetrix_prod
REDIS_URL=redis://redis:6379/0
GEMINI_API_KEY=your_gemini_api_key_here
PROMETHEUS_ENABLED=1
DEBUG=false
RELOAD=false
WORKERS=4
EOF
    print_warning "Please edit .env.production with your actual values before continuing."
    read -p "Press Enter to continue after editing .env.production..."
fi

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    print_success "Environment variables loaded from .env.production"
else
    print_error ".env.production file not found!"
    exit 1
fi

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans || true

# Remove old images (optional)
read -p "Do you want to remove old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing old Docker images..."
    docker system prune -f
fi

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.production.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Health checks
print_status "Performing health checks..."

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_error "Backend health check failed"
    docker-compose -f docker-compose.production.yml logs backend
    exit 1
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_error "Frontend health check failed"
    docker-compose -f docker-compose.production.yml logs frontend
    exit 1
fi

# Check database
if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U neuropetrix -d neuropetrix_prod > /dev/null 2>&1; then
    print_success "Database is healthy"
else
    print_error "Database health check failed"
    docker-compose -f docker-compose.production.yml logs db
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is healthy"
else
    print_error "Redis health check failed"
    docker-compose -f docker-compose.production.yml logs redis
    exit 1
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_success "Prometheus is healthy"
else
    print_warning "Prometheus health check failed (may still be starting)"
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    print_success "Grafana is healthy"
else
    print_warning "Grafana health check failed (may still be starting)"
fi

# Show service status
print_status "Service Status:"
docker-compose -f docker-compose.production.yml ps

# Show access URLs
echo ""
print_success "🎉 NeuroPETRIX Production Deployment Complete!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Prometheus:   http://localhost:9090"
echo "   Grafana:      http://localhost:3001 (admin/admin123)"
echo "   Kibana:       http://localhost:5601"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    docker-compose -f docker-compose.production.yml logs -f [service]"
echo "   Stop all:     docker-compose -f docker-compose.production.yml down"
echo "   Restart:      docker-compose -f docker-compose.production.yml restart [service]"
echo "   Update:       ./deploy.sh"
echo ""
echo "📊 Monitoring:"
echo "   System metrics are available at http://localhost:9090"
echo "   Grafana dashboards at http://localhost:3001"
echo "   Application logs in ./logs/ directory"
echo ""

# Optional: Run database migrations
read -p "Do you want to run database migrations? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running database migrations..."
    docker-compose -f docker-compose.production.yml exec backend python -m alembic upgrade head
    print_success "Database migrations completed"
fi

print_success "Deployment completed successfully! 🚀"