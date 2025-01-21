FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install KrakenD
RUN apt-get update && apt-get install -y ca-certificates dirmngr \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 5DE6FD698AD6FDD2 \
    && echo "deb https://repo.krakend.io/apt stable main" > /etc/apt/sources.list.d/krakend.list \
    && apt-get update \
    && apt-get install -y krakend

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for KrakenD configs
RUN mkdir -p /krakend-config

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    KRAKEND_CONFIG_PATH=/krakend-config

# Create healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the service
CMD ["python", "app.py"]
