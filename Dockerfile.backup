
# Use Miniconda as base image for conda support (needed for pinocchio)
FROM continuumio/miniconda3:latest

WORKDIR /app

# Install system dependencies for MediaPipe, OpenCV, and rendering
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-dri \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy environment.yml and install all dependencies (including pinocchio) via mamba/conda
COPY environment.yml ./
RUN conda install -y mamba -c conda-forge \
    && mamba env create -f environment.yml \
    && conda clean -afy

# Activate environment by default
SHELL ["/bin/bash", "-c"]
ENV PATH /opt/conda/envs/hand-teleop/bin:$PATH
ENV CONDA_DEFAULT_ENV=hand-teleop

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application with the correct environment
CMD ["/bin/bash", "-c", "conda run -n hand-teleop uvicorn backend.render_backend:app --host 0.0.0.0 --port 8000"]
