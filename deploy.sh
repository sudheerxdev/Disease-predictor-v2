#!/bin/bash
# Production deployment script
set -e

echo "================================================"
echo "Disease Predictor - Production Deployment"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment
source .env

# Verify required environment variables
required_vars=("SECRET_KEY" "DATABASE_URL" "GEMINI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env"
        exit 1
    fi
done

# Check if SECRET_KEY is default
if [ "$SECRET_KEY" = "your-secret-key-here" ]; then
    echo "❌ Error: SECRET_KEY is still set to default value!"
    echo "Please change SECRET_KEY in .env file"
    exit 1
fi

echo "✓ Configuration valid"
echo ""

# Build Docker images
echo "Building Docker images..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker-compose exec -T web python -c "from backend import create_app, db; app = create_app(); db.create_all()"

# Check health
echo "Checking application health..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✓ Application is healthy"
        break
    fi
    attempt=$((attempt + 1))
    echo "Waiting for application... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Application health check failed"
    docker-compose logs web
    exit 1
fi

echo ""
echo "================================================"
echo "✓ Deployment successful!"
echo "================================================"
echo ""
echo "Application is running on:"
echo "  - HTTP: http://localhost"
echo "  - HTTPS: https://yourdomain.com (once SSL is configured)"
echo ""
echo "Next steps:"
echo "1. Configure SSL/TLS certificate"
echo "2. Update Nginx configuration with your domain"
echo "3. Set up monitoring and alerts"
echo "4. Configure backups"
echo ""
echo "View logs:"
echo "  docker-compose logs -f web"
echo ""
