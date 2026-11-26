
# Use a lightweight Python base image
FROM python:3.12-slim

# Prevent Python from writing bytecode files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output appears immediately in logs
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies first for better Docker layer caching
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Document the port the application listens on
EXPOSE 5000

ENV PORT=5000

# Start Flask through Gunicorn, using the existing WSGI entry point
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} wsgi:app"]
