#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing system dependencies for WeasyPrint..."
# Note: Render allows apt-get in the build environment to install system libraries
apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libharfbuzz-dev \
    libfontconfig1 \
    libjpeg-dev \
    libpng-dev

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -e .

echo "Running database migrations..."
alembic upgrade head

echo "Build complete!"
