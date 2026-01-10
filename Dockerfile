# Dockerfile
FROM python:3.11-alpine

# Set workdir
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files and wait script
COPY . /app

EXPOSE 4010

# Start FastAPI only after db is ready
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4010", "--reload"]