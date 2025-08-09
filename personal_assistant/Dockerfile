# Personal Assistant Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose ports for the servers
EXPOSE 8000 8100 8200 8300

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Personal Assistant Services..."\n\
\n\
# Start all servers in background\n\
echo "Starting Meeting Server (Port 8100)..."\n\
python servers/meeting_server.py &\n\
\n\
echo "Starting Expense Server (Port 8200)..."\n\
python servers/expense_server.py &\n\
\n\
echo "Starting Orchestrator Server (Port 8300)..."\n\
python servers/orchestrator_server.py &\n\
\n\
echo "Starting API Server (Port 8000)..."\n\
python servers/api_server.py &\n\
\n\
# Wait for all background processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["./start.sh"]