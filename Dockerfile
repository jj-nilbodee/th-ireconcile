# Use Python 3.12 as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PORT=3000

# Install system dependencies and ensure all packages are up to date
RUN apt-get update \
    && apt-get upgrade -y
    # && apt-get install -y --no-install-recommends \
    #    build-essential \
    #    curl \
    # || (echo "Retrying apt-get install..."; apt-get update --fix-missing && apt-get install -y --no-install-recommends build-essential curl) \
    # && rm -rf /var/lib/apt/lists/*

RUN apt update && apt upgrade -y && apt install unzip nodejs npm -y

RUN npm install -g bun

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set up directory for uploads
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Build the frontend
RUN reflex init
RUN reflex export --frontend-only

# Default command
CMD reflex run --env prod
