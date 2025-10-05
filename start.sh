#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run the application
uvicorn run:app --reload --host 0.0.0.0 --port 8000
