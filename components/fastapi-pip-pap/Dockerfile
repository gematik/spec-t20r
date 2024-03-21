# Use the official Python image
FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app files to the container
COPY . .

# Expose the port where the FastAPI app will listen
EXPOSE 8200

# Command to run the FastAPI app
CMD ["python", "fastapi-pip-pap.py", "--configfile", "config.yaml", "--servername", "0.0.0.0", "--port", "8200"]
