# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app/backend

# Copy the backend directory contents into the container at /app/backend
COPY backend /app/backend

# Install dependencies
# We install gunicorn explicitly as it might not be in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV PORT=5001
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]
