#!/bin/bash

# Run migrations
alembic upgrade head

# Load initial data
python3 src/scripts/bootstrap.py

# Start the FastAPI server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000