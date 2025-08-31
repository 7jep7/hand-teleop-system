# Minimal Dockerfile for Render.com - Fast build
FROM python:3.10-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV DISABLE_WILOR=true
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "backend.render_backend:app", "--host", "0.0.0.0", "--port", "8000"]
