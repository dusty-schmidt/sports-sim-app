#!/bin/bash

# Start Backend
echo "Starting Backend..."
cd backend
export USE_SQLITE=True
export POSTGRES_SERVER=none
export POSTGRES_USER=none
export SECRET_KEY=dev_secret_key_unsafe
export FIRST_SUPERUSER=admin@example.com
export FIRST_SUPERUSER_PASSWORD=admin12345

# Install deps if needed (assuming uv is installed)
uv sync

# Run seeds (init db)
uv run python -m app.initial_data

# Start API in background
uv run fastapi dev app/main.py &
BACKEND_PID=$!

cd ..

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo "Systems running. Backend PID: $BACKEND_PID, Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop."

wait
