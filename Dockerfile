FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV USE_HTTPS=false
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "production_server.py"]
