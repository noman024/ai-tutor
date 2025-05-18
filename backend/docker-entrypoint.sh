#!/bin/bash
set -e

# Function to wait for postgres
wait_for_postgres() {
    echo "Waiting for PostgreSQL..."
    while ! nc -z db 5432; do
        sleep 0.1
    done
    echo "PostgreSQL started"
}

# Wait for postgres
wait_for_postgres

# Run migrations
echo "Running database migrations..."
cd /app/backend
PYTHONPATH=/app alembic upgrade head 2>&1 | tee /app/alembic.log

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload 