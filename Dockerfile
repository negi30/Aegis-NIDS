FROM python:3.10-slim

# Install system dependencies for Scapy and ML compilation
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8080

# Start the application
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}
