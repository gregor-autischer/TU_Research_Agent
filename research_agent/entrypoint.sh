#!/bin/bash
set -e

echo "Starting Research Agent..."

# Navigate to frontend
cd frontend

# Install dependencies if node_modules is missing (handled by volume, but good check)
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# Build frontend
echo "Building frontend assets..."
npm run build

# Move index.html to templates directory
echo "Configuring templates..."
mkdir -p ../web_app/templates/web_app
if [ -f "../web_app/static/web_app/index.html" ]; then
    mv ../web_app/static/web_app/index.html ../web_app/templates/web_app/index.html
    echo "Moved index.html to templates."
else
    echo "WARNING: index.html not found in build output!"
fi

# Go back to project root
cd ..

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Django development server
echo "Starting Django server on 0.0.0.0:8009..."
exec python manage.py runserver 0.0.0.0:8009
