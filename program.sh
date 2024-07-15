#!/bin/bash

# Check Python version and install if needed
echo "Checking Python version..."
current_python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_python_version="3.10"
echo "Current Python version: $current_python_version"

if [ "$(printf '%s\n' "$required_python_version" "$current_python_version" | sort -V | head -n1)" != "$required_python_version" ]; then
    echo "Installing Python $required_python_version..."
    sudo apt-get update
    sudo apt-get install -y python3.10
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    echo "Python $required_python_version installed successfully."
else
    echo "Python version is OK."
fi

# Check and install python3-venv package
if ! dpkg -l | grep -q "python3-venv"; then
    echo "Installing python3-venv package..."
    sudo apt-get install -y python3-venv
    echo "python3-venv package installed successfully."
fi

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created."
fi

echo "Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated."

# Install requirements
echo "Installing requirements..."
pip install -r requirements-pyppeteer.txt
echo "Requirements installed successfully."

echo "Starting..."
exec python -u program.py
