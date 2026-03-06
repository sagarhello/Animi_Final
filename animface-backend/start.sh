#!/bin/bash
set -e

echo "🎌 AnimeFace Backend — Starting up"
echo "=================================="

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
    echo "⚠️  Please review .env and update SECRET_KEY before production use!"
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

echo ""
echo "=================================="
echo "✅ AnimeFace is running!"
echo ""
echo "  📡 API:       http://localhost:8000"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo "  🌸 Redoc:     http://localhost:8000/redoc"
echo "  🌻 Flower:    http://localhost:5555"
echo "  🏥 Health:    http://localhost:8000/health"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f api"
echo "=================================="
