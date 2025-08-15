FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.deploy_api:app", "--host", "0.0.0.0", "--port", "8000"]
