# Minimal Dockerfile for Render.com - Fast build
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for headless OpenCV (no GUI/OpenGL)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables for headless operation
ENV DISABLE_WILOR=true
ENV PYTHONPATH=/app
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
ENV QT_QPA_PLATFORM=offscreen

# Run the application
CMD ["uvicorn", "backend.render_backend:app", "--host", "0.0.0.0", "--port", "8000"]
