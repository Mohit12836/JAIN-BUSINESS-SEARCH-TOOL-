FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Python environment settings
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Copy and install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy project files
COPY . .

# Ensure data directories exist
RUN mkdir -p /app/data /app/database

# Expose default port
EXPOSE 8000

# Run FastAPI app with dynamic port binding for Render/Railway/Cloud
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
