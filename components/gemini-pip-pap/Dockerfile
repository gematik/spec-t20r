# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 8600

# Run the main application
CMD ["uvicorn", "gemini-pip-pap:app", "--host", "0.0.0.0", "--port", "8600", "--reload"]
