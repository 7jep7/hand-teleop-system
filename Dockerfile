# Optimized Dockerfile for Render.com - OpenCV compatible
FROM python:3.10

WORKDIR /app

# Install essential system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
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
ENV LIBGL_ALWAYS_INDIRECT=1
ENV LIBGL_ALWAYS_SOFTWARE=1

# Run the application
CMD ["uvicorn", "backend.render_backend:app", "--host", "0.0.0.0", "--port", "8000"]
