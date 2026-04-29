#!/bin/bash

# Production Deployment Script
# This script handles deployment of the SDLC Multi-Agent Backend Builder

set -e

echo "🚀 Starting deployment process..."

# Configuration
DOCKER_IMAGE="sdlc-multi-agent:latest"
CONTAINER_NAME="sdlc-multi-agent-prod"
PORT="8001"
FRONTEND_CONTAINER="sdlc-frontend-prod"
FRONTEND_PORT="8501"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Check environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ GEMINI_API_KEY environment variable is not set${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment check passed${NC}"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop $CONTAINER_NAME $FRONTEND_CONTAINER 2>/dev/null || true
docker rm $CONTAINER_NAME $FRONTEND_CONTAINER 2>/dev/null || true

# Pull latest image
echo "📥 Pulling latest Docker image..."
docker pull $DOCKER_IMAGE || echo -e "${YELLOW}⚠️ Could not pull image, using local${NC}"

# Start backend service
echo "🔧 Starting backend service..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8001 \
    -e GEMINI_API_KEY=$GEMINI_API_KEY \
    -e DEBUG=False \
    --restart=always \
    --health-cmd="curl -f http://localhost:8001/ || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    $DOCKER_IMAGE

# Wait for backend to be healthy
echo "⏳ Waiting for backend to be healthy..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:$PORT/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Backend failed to become healthy${NC}"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Start frontend service (optional)
echo "🎨 Starting frontend service..."
docker run -d \
    --name $FRONTEND_CONTAINER \
    -p $FRONTEND_PORT:8501 \
    --restart=always \
    $DOCKER_IMAGE \
    streamlit run app.py

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "📍 Service URLs:"
echo "   Backend API: http://localhost:$PORT"
echo "   Frontend UI: http://localhost:$FRONTEND_PORT"
echo ""
echo "📊 To view logs:"
echo "   docker logs -f $CONTAINER_NAME"
echo "   docker logs -f $FRONTEND_CONTAINER"
echo ""
echo "🛑 To stop services:"
echo "   docker stop $CONTAINER_NAME $FRONTEND_CONTAINER"
