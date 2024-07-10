#!/bin/bash

# Activate virtual environment if not activated
if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
fi

echo "Starting..."

python app.py
