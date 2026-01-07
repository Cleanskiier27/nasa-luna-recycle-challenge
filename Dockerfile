FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install build/test deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Run tests by default
CMD ["pytest", "-q"]
